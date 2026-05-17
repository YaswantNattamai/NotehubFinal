import { Platform } from "react-native";
import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";

// For production, set EXPO_PUBLIC_API_URL in your environment or .env file
<<<<<<< HEAD
const DEFAULT_IP = "172.29.16.221"; // Change this to your local IP for mobile
=======
const DEFAULT_IP = "10.205.111.177"; // Change this to your local IP for mobile
>>>>>>> fcb8735c273514976c0dfd8cd372d130459282ff
export const BASE_URL = process.env.EXPO_PUBLIC_API_URL ||
  (Platform.OS === "web" ? "http://localhost:8000" : `http://${DEFAULT_IP}:8000`);

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 600000, // 10 minutes — multi-page LLaVA OCR can take 30-60s per image
});

api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
