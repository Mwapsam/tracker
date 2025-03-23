"use server";

import { cookies } from "next/headers";
import axios from "axios";
import { BASE_URL } from ".";

export const getToken = async (type: string) => {
  const cookieStore = cookies();
  return (await cookieStore).get(`${type}Token`)?.value;
};

export const storeToken = async (token: string, type: "access" | "refresh") => {
  const cookieStore = cookies();
  (await cookieStore).set(`${type}Token`, token, {
    path: "/",
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
  });
};

const removeTokens = async () => {
  const cookieStore = cookies();
  (await cookieStore).delete("accessToken");
  (await cookieStore).delete("refreshToken");
};

export const axiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

axiosInstance.interceptors.request.use(async (config) => {
  const token = await getToken("access");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const refreshInstance = axios.create({
  baseURL: process.env.DJANGO_API_URL,
  headers: { "Content-Type": "application/json" },
});

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response?.status === 401 ||
      (error.response?.status === 403 &&
        !originalRequest._retry &&
        !originalRequest.url.includes("/api/token/refresh/"))
    ) {
      originalRequest._retry = true;
      const refreshToken = await getToken("refresh");
      if (!refreshToken) {
        await removeTokens();
        return Promise.reject(error);
      }

      try {
        const { data } = await refreshInstance.post("/api/token/refresh/", {
          refresh: refreshToken,
        });

        await storeToken(data.access, "access");
        if (data.refresh) {
          await storeToken(data.refresh, "refresh");
        }
        originalRequest.headers.Authorization = `Bearer ${data.access}`;
        axiosInstance.defaults.headers.common.Authorization = `Bearer ${data.access}`;
        return axiosInstance(originalRequest);
      } catch (err) {
        await removeTokens();

        return Promise.reject(err);
      }
    }
    return Promise.reject(error);
  }
);
