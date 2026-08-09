import { useRef, useState } from "react";

import {
  uploadDocuments,
} from "../api/client";

import type {
  Document,
} from "../types/api";


interface UploadZoneProps {
  onUploaded: (
    documents: Document[],
  ) => void;
}


function UploadZone({
  onUploaded,
}: UploadZoneProps) {

  const inputRef = useRef<HTMLInputElement>(
    null,
  );

  const [uploading, setUploading] = useState(
    false,
  );

  const [error, setError] = useState<
    string | null
  >(null);


  async function handleFiles(
    files: FileList | null,
  ) {

    if (!files || files.length === 0) {
      return;
    }

    setError(null);
    setUploading(true);

    try {

      const selectedFiles = Array.from(
        files,
      );

      const invalidFile = selectedFiles.find(
        (file) =>
          file.type !== "application/pdf",
      );

      if (invalidFile) {
        throw new Error(
          `${invalidFile.name} is not a PDF.`,
        );
      }

      const tooLarge = selectedFiles.find(
        (file) =>
          file.size > 10 * 1024 * 1024,
      );

      if (tooLarge) {
        throw new Error(
          `${tooLarge.name} exceeds the 10 MB limit.`,
        );
      }

      const documents =
        await uploadDocuments(
          selectedFiles,
        );

      onUploaded(documents);

    } catch (err) {

      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "Something went wrong while uploading.",
        );
      }

    } finally {

      setUploading(false);

      if (inputRef.current) {
        inputRef.current.value = "";
      }
    }
  }


  return (
    <div>

      <button
        className="upload-button"
        onClick={() =>
          inputRef.current?.click()
        }
        disabled={uploading}
      >
        {uploading
          ? "Processing..."
          : "+ Upload PDFs"}
      </button>


      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        multiple
        hidden
        onChange={(event) =>
          handleFiles(
            event.target.files,
          )
        }
      />


      {error && (
        <div className="upload-error">
          {error}
        </div>
      )}

    </div>
  );
}


export default UploadZone;