import axios from "axios";

const BASE_URL =
  process.env.REACT_APP_API_BASE_URL?.trim() || "http://127.0.0.1:8000";

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 120000,
});

export const formatApiError = (error, fallbackMessage) => {
  if (error.response?.data?.detail) {
    return String(error.response.data.detail);
  }
  if (error.response?.data?.message) {
    return String(error.response.data.message);
  }
  if (error.code === "ECONNABORTED") {
    return "Request timed out. The analysis is taking longer than expected.";
  }
  if (error.message) {
    return error.message;
  }
  return fallbackMessage;
};

export const analyzeQuery = async (query, uploadedFile = null) => {
  const response = await client.post("/analyze", {
    query: query,
    file: uploadedFile,
  });
  return response.data;
};

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await client.post("/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};