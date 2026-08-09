import type {
  Source,
} from "../types/api";

import {
  getPdfUrl,
} from "../api/client";


interface SourceCardProps {
  source: Source;
  onTranslate: (
    source: Source,
  ) => void;
}


function SourceCard({
  source,
  onTranslate,
}: SourceCardProps) {

  const pdfUrl =
    `${getPdfUrl(source.document_id)}` +
    `#page=${source.page_number}`;


  return (
    <div className="source-card">

      <div>

        <div className="source-file">
          📄 {source.file_name}
        </div>

        <div className="source-page">
          Page {source.page_number}
        </div>

      </div>


      <div className="source-actions">

        <a
          href={pdfUrl}
          target="_blank"
          rel="noreferrer"
          className="source-button"
        >
          Open
        </a>

        <button
          className="source-button"
          onClick={() =>
            onTranslate(source)
          }
        >
          Translate
        </button>

      </div>

    </div>
  );
}


export default SourceCard;