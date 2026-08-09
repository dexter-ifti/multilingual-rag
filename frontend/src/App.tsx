import { useEffect, useState } from "react";
import UploadZone from "./components/UploadZone";
import Chat from "./components/Chat";
import {
  getDocuments,
} from "./api/client";

import type {
  Document,
} from "./types/api";

import "./App.css";


function App() {

  const [documents, setDocuments] = useState<Document[]>([]);

  useEffect(() => {

    getDocuments()
      .then(setDocuments)
      .catch(console.error);

  }, []);


  return (
    <div className="app">

      <header className="header">

        <div>
          <h1>Document QA</h1>

          <p>
            Ask questions across multilingual PDFs
          </p>
        </div>

      </header>


      <main className="workspace">

        <aside className="sidebar">

          <div className="sidebar-header">

            <h2>Documents</h2>
            
            <span>
              {documents.length}
            </span>
            <UploadZone
               onUploaded={(newDocuments) =>
                 setDocuments((current) => [
                   ...current,
                   ...newDocuments,
                 ])
               }
             />
          </div>


          <div className="document-list">

            {documents.length === 0 ? (

              <div className="empty-documents">

                <p>No documents yet.</p>

                <span>
                  Upload a PDF to get started.
                </span>

              </div>

            ) : (

              documents.map((document) => (

                <div
                  className="document-item"
                  key={document.document_id}
                >

                  <div className="document-icon">
                    PDF
                  </div>

                  <div>

                    <strong>
                      {document.file_name}
                    </strong>

                    <span>
                      {document.page_count} pages
                    </span>

                  </div>

                </div>

              ))

            )}

          </div>

        </aside>


        <section className="chat-area">

          <Chat/>

        </section>

      </main>

    </div>
  );
}


export default App;