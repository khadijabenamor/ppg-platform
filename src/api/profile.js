import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000/api/auth",
});

export const getProfile = (token) =>
  API.get("/profile/", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

export const updateProfile = (token, data) =>
  API.patch("/profile/", data, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });