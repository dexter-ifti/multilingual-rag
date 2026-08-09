import {
  FormEvent,
  useState,
} from "react";

import {
  askQuestion,
} from "../api/client";

import type {
  ChatResponse,
} from "../types/api";

import SourceCard from "./SourceCard";

import TranslationPanel from "./TranslationPanel";


interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
}


function Chat() {

  const [
    messages,
    setMessages,
  ] = useState<ChatMessage[]>([]);


  const [
    question,
    setQuestion,
  ] = useState("");


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    error,
    setError,
  ] = useState<string | null>(null);

  const [
    translationSource,
    setTranslationSource,
  ] = useState<Source | null>(null);

  async function handleSubmit(
    event: FormEvent,
  ) {

    event.preventDefault();

    const trimmed =
      question.trim();

    if (!trimmed || loading) {
      return;
    }

    setError(null);

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
    };

    setMessages((current) => [
      ...current,
      userMessage,
    ]);

    setQuestion("");
    setLoading(true);

    try {

      const response =
        await askQuestion(trimmed);

      const assistantMessage:
        ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.answer,
          response,
        };

      setMessages((current) => [
        ...current,
        assistantMessage,
      ]);

    } catch (err) {

      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "Failed to get an answer.",
        );
      }

    } finally {

      setLoading(false);
    }
  }


  function handleTranslate(
    source: Source,
  ) {
    console.log(
      "Translate:",
      source,
    );
  }

  return (
    <div className="chat-container">

      <div className="messages">

        {messages.length === 0 && (

          <div className="chat-empty">

            <div className="hero-icon">
              ✦
            </div>

            <h2>
              Ask anything about your documents
            </h2>

            <p>
              Ask questions in English.
              I'll find the relevant passages
              from your uploaded documents.
            </p>

          </div>
        )}


        {messages.map((message) => (

          <div
            key={message.id}
            className={
              `message-row ${message.role}`
            }
          >

            <div className="message">

              <div className="message-label">
                {message.role === "user"
                  ? "You"
                  : "AI"}
              </div>

              <div className="message-content">
                {message.content}
              </div>


              {message.role ===
                "assistant" &&
                message.response && (

                <div className="sources">

                  <div className="sources-title">
                    Sources
                  </div>


                  {message.response.sources.map(
                    (source, index) => (
                  
                      <SourceCard
                        key={`${source.document_id}-${source.page_number}-${index}`}
                        source={source}
                        onTranslate={handleTranslate}
                      />
                  
                    )
                  )}

                </div>
              )}

            </div>

          </div>

        ))}


        {loading && (

          <div className="message-row assistant">

            <div className="message">

              <div className="message-label">
                AI
              </div>

              <div className="typing">
                Thinking...
              </div>

            </div>

          </div>

        )}

      </div>


      {error && (
        <div className="chat-error">
          {error}
        </div>
      )}


      <form
        className="chat-input-area"
        onSubmit={handleSubmit}
      >

        <input
          value={question}
          onChange={(event) =>
            setQuestion(
              event.target.value,
            )
          }
          placeholder="Ask a question about your documents..."
          disabled={loading}
        />

        <button
          type="submit"
          disabled={
            loading ||
            !question.trim()
          }
        >
          ↑
        </button>

      </form>
      {translationSource && (
        <TranslationPanel
          source={translationSource}
          onClose={() =>
            setTranslationSource(null)
          }
        />
      )}
    </div>
  );
}


export default Chat;