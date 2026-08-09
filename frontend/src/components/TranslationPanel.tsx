import { useEffect, useState } from "react";

import {
  translatePage,
} from "../api/client";

import type {
  Source,
  TranslationResponse,
} from "../types/api";


interface TranslationPanelProps {
  source: Source;
  onClose: () => void;
}


function TranslationPanel({
  source,
  onClose,
}: TranslationPanelProps) {

  const [
    result,
    setResult,
  ] = useState<TranslationResponse | null>(
    null,
  );


  const [
    loading,
    setLoading,
  ] = useState(true);


  const [
    error,
    setError,
  ] = useState<string | null>(null);


  useEffect(() => {

    let cancelled = false;


    async function loadTranslation() {

      try {

        setLoading(true);

        const response =
          await translatePage(
            source.document_id,
            source.page_number,
          );

        if (!cancelled) {
          setResult(response);
        }

      } catch (err) {

        if (!cancelled) {

          if (err instanceof Error) {
            setError(err.message);
          } else {
            setError(
              "Failed to translate page.",
            );
          }
        }

      } finally {

        if (!cancelled) {
          setLoading(false);
        }

      }
    }


    loadTranslation();


    return () => {
      cancelled = true;
    };

  }, [
    source.document_id,
    source.page_number,
  ]);


  return (
    <aside className="translation-panel">

      <div className="translation-header">

        <div>

          <div className="translation-title">
            {source.file_name}
          </div>

          <div className="translation-page">
            Page {source.page_number}
          </div>

        </div>


        <button
          className="close-button"
          onClick={onClose}
        >
          ×
        </button>

      </div>


      <div className="translation-body">

        {loading && (

          <div className="translation-loading">
            Translating page...
          </div>

        )}


        {error && (

          <div className="translation-error">
            {error}
          </div>

        )}


        {result && (

          <>

            <section className="translation-section">

              <div className="translation-label">
                Original
              </div>

              <div className="translation-text original">
                {result.original_text}
              </div>

            </section>


            <section className="translation-section">

              <div className="translation-label">
                English
              </div>

              <div className="translation-text">
                {result.translation}
              </div>

            </section>

          </>

        )}

      </div>

    </aside>
  );
}


export default TranslationPanel;