from server.models.interfaces import BaseLLMConfigurationInterface
from server.helpers import get_config
from server.models.enums import LLMProvider, LLMExecutionMode
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_cohere import ChatCohere
from langchain_ollama import ChatOllama

# ========================
# MODERN IMPORTS (langchain >= 0.3.x)
# No deprecated langchain.memory or langchain.schema
# ========================
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field


# ========================
# CUSTOM SUMMARY BUFFER MEMORY
# Replaces deprecated ConversationSummaryBufferMemory using the modern
# BaseChatMessageHistory API as recommended in the langchain 0.3 migration guide.
#
# Behavior (identical to the old class):
#   - Keeps recent messages verbatim in a buffer up to `max_token_limit`
#   - When limit is exceeded, summarizes all buffered messages into a rolling
#     summary SystemMessage using the same LLM
#   - System message is always injected first by LLMController, never stored here
# ========================
class SummaryBufferMessageHistory(BaseChatMessageHistory, BaseModel):
    """
    Modern replacement for ConversationSummaryBufferMemory.
    Extends BaseChatMessageHistory so it is compatible with the full
    langchain_core runnable / history ecosystem.
    """
    messages: List[BaseMessage] = Field(default_factory=list)
    moving_summary_buffer: str = Field(default="")
    max_token_limit: int = Field(default=2400)
    llm: Any = Field(default=None)          # same LLM used for summarization

    class Config:
        arbitrary_types_allowed = True

    # ---- token estimation (same formula as LLMController) ----
    def _estimate_tokens(self, text: str) -> int:
        return int(len(text) / 4)

    def _count_tokens(self, msgs: List[BaseMessage]) -> int:
        return sum(self._estimate_tokens(m.content) for m in msgs)

    # ---- summarization prompt (mirrors the old SummarizerMixin prompt) ----
    def _summarize(self, existing_summary: str, new_messages: List[BaseMessage]) -> str:
        """
        Call the LLM to produce a new rolling summary from:
          - the existing summary (may be empty)
          - the new messages that overflowed the buffer
        """
        lines = "\n".join(
            f"{'Human' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
            for m in new_messages
        )
        prompt_text = (
            "Progressively summarize the lines of conversation provided, "
            "adding onto the previous summary and returning a new summary.\n\n"
            f"CURRENT SUMMARY:\n{existing_summary}\n\n"
            f"NEW LINES:\n{lines}\n\n"
            "NEW SUMMARY:"
        )
        response = self.llm.invoke([HumanMessage(content=prompt_text)])
        return response.content.strip()

    # ---- BaseChatMessageHistory interface ----
    def add_messages(self, messages: List[BaseMessage]) -> None:
        """
        Add new messages and prune if over the token budget by summarizing.
        Called automatically after every turn.
        """
        self.messages.extend(messages)

        # Prune: if buffer exceeds limit, summarize the oldest messages
        while self._count_tokens(self.messages) > self.max_token_limit and len(self.messages) >= 2:
            # Take the two oldest messages (one Human + one AI turn)
            to_summarize = self.messages[:2]
            self.messages = self.messages[2:]
            if self.llm is not None:
                self.moving_summary_buffer = self._summarize(
                    self.moving_summary_buffer, to_summarize
                )

    def clear(self) -> None:
        """Reset the memory completely."""
        self.messages = []
        self.moving_summary_buffer = ""


class LLMController(BaseLLMConfigurationInterface):
    def __init__(self, params: Dict[str, Any] = None, system_message: str = None):
        if params is None:
            params = {"max_tokens": get_config().MAX_TOKENS, "temperature": get_config().TEMPERATURE}
        BaseLLMConfigurationInterface.__init__(self, params)
        self.config = get_config()
        self.SYSTEM_MESSAGE = SystemMessage(content=system_message.strip() if system_message else "")

        # ========================
        # MEMORY INITIALIZATION
        # ========================
        # Memory is initialized as None here; it is created after setup()
        # because it requires the LLM client to be ready (used for summarization).
        # SummaryBufferMessageHistory (replaces ConversationSummaryBufferMemory):
        #   - Keeps recent messages in a raw buffer up to `max_token_limit`
        #   - Summarizes older messages beyond the limit into a single summary
        #   - Always retains the system message via memory_key injection
        #   - Best choice for local Ollama models with small context windows
        self._memory: Optional[SummaryBufferMessageHistory] = None

    def setup(self) -> bool:
        """
        setup Model (local or remote)
        Returns: True if success
        """
        # ========================
        # REMOTE SETUP :
        # ========================
        if self.config.LLM_MODE == LLMExecutionMode.REMOTE.value:
            self.mode = LLMExecutionMode.REMOTE.value

            # ========================
            # 1) GEMINI SETUP  :
            # ========================
            if self.config.LLM_PROVIDER == LLMProvider.GEMINI.value:
                self.api_key = self.config.GEMINI_API_KEY
                self.model_id = self.config.GEMINI_MODEL_ID
                self.base_url = None
                self.client = ChatGoogleGenerativeAI(
                    model=self.model_id,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    api_key=self.api_key
                )
                self._is_connected = True

            # ========================
            # 2) OPENAI SETUP :
            # ========================
            elif self.config.LLM_PROVIDER == LLMProvider.OPENAI.value:
                self.api_key = self.config.OPENAI_API_KEY
                self.model_id = self.config.OPENAI_MODEL_ID
                self.base_url = self.config.OPEN_AI_BASE_URL
                self.client = ChatOpenAI(
                    model=self.model_id,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                self._is_connected = True

            # ========================
            # 3) CLAUDE SETUP :
            # ========================
            elif self.config.LLM_PROVIDER == LLMProvider.CLAUDE.value:
                self.api_key = self.config.CLAUDE_API_KEY
                self.model_id = self.config.CLAUDE_MODEL_ID
                self.base_url = None
                self.client = ChatAnthropic(
                    model=self.model_id,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    api_key=self.api_key,
                )
                self._is_connected = True

            # ========================
            # 4) COHERE SETUP :
            # ========================
            elif self.config.LLM_PROVIDER == LLMProvider.COHERE.value:
                self.api_key = self.config.COHERE_API_KEY
                self.model_id = self.config.COHERE_MODEL_ID
                self.client = ChatCohere(
                    model=self.model_id,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    cohere_api_key=self.api_key,
                )
                self._is_connected = True

            # ========================
            # UNKNOWN PROVIDER :
            # ========================
            else:
                self._is_connected = False
                raise ValueError(f"Unknown provider: {self.config.LLM_PROVIDER}")

        # ========================
        # LOCAL SETUP :
        # ========================
        elif self.config.LLM_MODE == LLMExecutionMode.LOCAL.value:
            self.mode = LLMExecutionMode.LOCAL.value
            self.api_key = self.config.OLLAMA_API_KEY if hasattr(self.config, 'OLLAMA_API_KEY') else None
            self.model_id = self.config.OLLAMA_MODEL_ID
            self.base_url = self.config.OLLAMA_BASE_URL
            self.client = ChatOllama(
                model=self.model_id,
                base_url=self.base_url,
                temperature=self.temperature,
                num_predict=self.max_tokens,
                num_ctx=self.config.CONTEXT_WINDOW if hasattr(self.config, 'CONTEXT_WINDOW') else 8192,
            )
            self._is_connected = True

        # ========================
        # UNKNOWN MODE :
        # ========================
        else:
            self._is_connected = False
            raise ValueError(f"Unknown execution mode: {self.config.LLM_MODE}")

        # ========================
        # MEMORY SETUP (after client is ready)
        # ========================
        # max_token_limit: how many tokens to keep in raw buffer before summarizing.
        # Set to ~40% of MAX_INPUT_TOKENS so there is always room for the system
        # message + new user turn + model response within the context window.
        max_input_tokens = self.config.MAX_INPUT_TOKENS if hasattr(self.config, 'MAX_INPUT_TOKENS') else 6000
        memory_token_limit = int(max_input_tokens * 0.4)

        self._memory = SummaryBufferMessageHistory(
            llm=self.client,                      # uses the same LLM to produce summaries
            max_token_limit=memory_token_limit,   # token budget for raw recent messages
        )

        return self._is_connected

    def update_system_message(self, text: str):
        """
        Create system message for LLM
        Args:
            text: system prompt text
        Update: SystemMessage object
        """
        self.SYSTEM_MESSAGE = SystemMessage(content=text.strip())

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        Args:
            text: input text
        Returns: estimated token count
        """
        return int(len(text) / 4)

    def _count_tokens(self, messages: List) -> int:
        """
        Count total tokens in message list
        Args:
            messages: list of messages
        Returns: total token count
        """
        total = 0
        for msg in messages:
            total += self._estimate_tokens(msg.content)
        return total

    # ========================
    # MEMORY HELPERS
    # ========================
    def _build_messages_from_memory(self) -> List[BaseMessage]:
        """
        Build the full message list by combining:
          1. System message (always first)
          2. Summary of old turns (if any) injected as a SystemMessage addendum
          3. Recent raw messages kept in the buffer

        NOTE: This method returns ONLY previous turns (system + past history).
              The current human message must be appended ONCE by the caller.

        Returns: list of BaseMessage objects ready to pass to the LLM
        """
        memory_messages: List[BaseMessage] = self._memory.messages
        summary_text: str = self._memory.moving_summary_buffer  # may be "" if buffer not full yet

        messages: List[BaseMessage] = []

        # 1) System message always comes first
        messages.append(self.SYSTEM_MESSAGE)

        # 2) If a rolling summary exists, prepend it as an addendum to context
        if summary_text and summary_text.strip():
            summary_note = SystemMessage(
                content=f"[Summary of earlier conversation]:\n{summary_text.strip()}"
            )
            messages.append(summary_note)

        # 3) Append the recent buffer messages (HumanMessage / AIMessage pairs)
        #    These are ONLY completed previous turns — the current human message
        #    is NOT stored in memory yet, so no duplication occurs here.
        messages.extend(memory_messages)

        return messages

    def _save_turn_to_memory(self, user_input: str, ai_response: str):
        """
        Persist the latest human/AI turn into the memory buffer.
        Called AFTER the LLM responds so the current turn is never
        included in the context built by _build_messages_from_memory()
        during the same invocation.

        Args:
            user_input: the user's raw text
            ai_response: the model's response text
        """
        self._memory.add_messages([
            HumanMessage(content=user_input.strip()),
            AIMessage(content=ai_response.strip()),
        ])

    def release_history(self):
        """
        Release conversation history
        """
        self.history = []

        # ========================
        # MEMORY RESET
        # ========================
        if self._memory is not None:
            self._memory.clear()

    def generate_response(self, user_input: str) -> str:
        """
        Core generation method.

        Message flow per turn:
          1. Build context from memory  → [system, (summary), ...past turns]
          2. Append current human msg   → [..., HumanMessage(current)]   ← ONCE
          3. Invoke LLM
          4. Save completed turn to memory (human + AI) for future turns

        Args:
            user_input: current user message
        Returns: Generated text
        """
        if not self._is_connected:
            raise ConnectionError("LLM Client is not connected. Please run setup() first.")
        if self.SYSTEM_MESSAGE is None or len(self.SYSTEM_MESSAGE.content.strip()) == 0:
            raise ValueError("System message is not initialized. Please run update_system_message() first.")
        if not user_input.strip():
            raise ValueError("User input is empty.")

        # ========================
        # HISTORY: append-only log — never trimmed or modified.
        # Used only for record-keeping; never sent to the LLM directly.
        # ========================
        if not self.history:
            self.history = [self.SYSTEM_MESSAGE]

        human_message = HumanMessage(content=f"Interview Question: {user_input.strip()}")
        self.history.append(human_message)

        # ========================
        # MEMORY: build compressed context from PAST turns only,
        # then append the CURRENT human message exactly once.
        #
        # _build_messages_from_memory() returns:
        #   [system, (optional summary), ...completed past turns]
        #
        # _save_turn_to_memory() is called AFTER invoke, so the current
        # human message is never inside _memory.messages during this call.
        # This guarantees no duplication.
        # ========================
        if self._memory is not None:
            messages_to_send = self._build_messages_from_memory()
            messages_to_send.append(human_message)   # append current turn ONCE
        else:
            # Fallback: use the full history log directly
            messages_to_send = list(self.history)

        try:
            response = self.client.invoke(messages_to_send)
        except Exception as e:
            if "exceed context window" in str(e) or "context" in str(e).lower():
                # ========================
                # MEMORY FALLBACK: clear memory + retry with only system + current turn.
                # history is NOT touched — it remains the complete log.
                # ========================
                if self._memory is not None:
                    self._memory.clear()
                response = self.client.invoke([self.SYSTEM_MESSAGE, human_message])
            else:
                raise

        # ========================
        # HISTORY: append AI response to keep the complete log intact
        # ========================
        self.history.append(AIMessage(content=response.content))

        # ========================
        # MEMORY: persist this completed turn (human + AI) so future calls
        # can include it in context or summarize it if the buffer overflows.
        # Saving happens HERE (after invoke) — never before — so the current
        # human message is absent from memory during _build_messages_from_memory()
        # above, eliminating any risk of duplication.
        # ========================
        if self._memory is not None:
            self._save_turn_to_memory(user_input, response.content)

        return response.content

    def cleanup(self):
        """
        Release resources
        """
        self.client = None
        self.history = []
        self._is_connected = False
        self.SYSTEM_MESSAGE = None

        # ========================
        # MEMORY CLEANUP
        # ========================
        if self._memory is not None:
            self._memory.clear()
        self._memory = None