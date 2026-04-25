import React, { useRef, useState } from "react";

import { uploadFile } from "../api";

function FileUpload({ onFileUpload, disabled }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError("");
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError("");

    try {
      const result = await uploadFile(selectedFile);
      onFileUpload(result.filename, result.original_name || selectedFile.name);
      setSelectedFile(null);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    } catch (error) {
      console.error("Upload error:", error);
      const message =
        error.response?.data?.detail || error.message || "Upload failed";
      setError(message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-box">
      <h3>Upload Dataset</h3>
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.xlsx,.xls,.json"
        onChange={handleFileChange}
        disabled={disabled || uploading}
      />
      <button
        onClick={handleUpload}
        disabled={!selectedFile || disabled || uploading}
        className="btn btn-upload"
      >
        {uploading ? "Uploading..." : "Upload Dataset"}
      </button>
      {selectedFile && (
        <p className="upload-details">
          Selected: {selectedFile.name}
        </p>
      )}
      {error && (
        <p className="upload-details upload-error">
          Upload error: {error}
        </p>
      )}
    </div>
  );
}

export default FileUpload;
