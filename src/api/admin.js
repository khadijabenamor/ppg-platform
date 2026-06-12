import axios from "axios";

const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token");

    return token
        ? { Authorization: `Bearer ${token}` }
        : {};
};

const API = axios.create({
    baseURL: "http://127.0.0.1:8000/api/auth",
    headers: {
        "Content-Type": "application/json",
    },
});

export const getDashboard = () =>
    API.get("/admin-dashboard/", {
        headers: getAuthHeaders(),
    });

export const getStatistics = (days = 30) =>
    API.get(`/admin/statistics/?days=${days}`, {
        headers: getAuthHeaders(),
    });   

 