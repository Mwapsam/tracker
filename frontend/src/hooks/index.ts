"use server";

import { Trip } from "@/utils";
import { axiosInstance } from "@/utils/session";
import axios from "axios";

export const fetchTrip = async (): Promise<Trip[]> => {
  const response = await axiosInstance.get(`/api/trips/`);
  return response.data;
};

export const createTrip = async (tripData: TripFormData): Promise<Trip> => {
  try {
    const response = await axiosInstance.post(`/api/trips/`, tripData);

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error(
        "Error creating trip:",
        error.response?.data || error.message
      );
    } else {
      console.error("Error creating trip:", error);
    }
    throw error;
  }
};

export const startTrip = async (tripId: number): Promise<Trip | undefined> => {
  try {
    const response = await axiosInstance.post(
      `/api/trips/${tripId}/start/`,
      {}
    );
    return response.data;
  } catch (error) {
    if (error instanceof Error) {
      console.error("Error starting trip:", error.message);
    } else {
      console.error("Error starting trip:", error);
    }
    return undefined;
  }
};

export const completeTrip = async (tripId: number): Promise<Trip> => {
  const response = await axiosInstance.post(`/api/trips/${tripId}/complete/`);
  return response.data;
};

export const updateLocation = async (
  tripId: number,
  location: string
): Promise<Trip> => {
  const response = await axiosInstance.patch(
    `/api/trips/${tripId}/update_location/`,
    {
      current_location: location,
    }
  );
  return response.data;
};

interface TripFormData {
  current_location: string;
  pickup_location: string;
  dropoff_location: string;
  current_cycle_used: number;
  vehicle: string;
  driver: string | null;
}
