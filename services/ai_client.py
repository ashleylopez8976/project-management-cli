import ollama


class OllamaChatClient:
    """Provide reusable communication with a local Ollama model."""

    def __init__(self, model_name="llama3.2"):
        """Store the model name and initialize conversation history."""
        self.model_name = model_name
        self.history = []

    def send(self, prompt):
        """Send a prompt and return usable assistant text."""
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        previous_count = len(self.history)
        self.history.append({
            "role": "user",
            "content": prompt.strip(),
        })

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=self.history,
            )

            if isinstance(response, dict):
                message = response.get("message")
            else:
                message = getattr(response, "message", None)

            if isinstance(message, dict):
                content = message.get("content")
            else:
                content = getattr(message, "content", None)

            if not isinstance(content, str) or not content.strip():
                raise ValueError("The model returned an empty response.")

            content = content.strip()
            self.history.append({
                "role": "assistant",
                "content": content,
            })
            return content

        except Exception as error:
            del self.history[previous_count:]
            raise RuntimeError(
                "AI service request failed. Check that Ollama is "
                f"running and '{self.model_name}' is installed. "
                f"Details: {error}"
            ) from error

    def reset(self):
        """Clear the conversation history."""
        self.history.clear()

    def message_count(self):
        """Return the number of stored conversation messages."""
        return len(self.history)

    def get_transcript(self):
        """Return independent copies of stored messages."""
        return [message.copy() for message in self.history]