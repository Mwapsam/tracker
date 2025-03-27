"use client";

import React, {
  useState,
  ChangeEvent,
  FormEvent,
  useRef,
  useEffect,
  useCallback,
} from "react";
import { Box, Flex, Card, Text, Heading, Button } from "@radix-ui/themes";
import Wrapper from "@/wrapper";
import createLog from "@/app/actions/createLog";
import { Driver, LogEntryFormData, Vehicle } from "@/utils";
import { useRouter } from "next/navigation";

type LogEntryFormProps = {
  drivers: Driver[];
  vehicles: Vehicle[];
};

export default function LogEntryForm({ drivers, vehicles }: LogEntryFormProps) {
  const [formData, setFormData] = useState<LogEntryFormData>({
    date: "",
    driver: {
      id: "",
      user: { first_name: "", last_name: "" },
    },
    vehicle: { id: "", truck_number: "", trailer_number: "" },
    start_odometer: "",
    end_odometer: "",
    remarks: "",
    signature: "",
    adverse_conditions: false,
    duty_statuses: [],
  });

  const router = useRouter();
  const autocompleteRefs = useRef<HTMLInputElement[]>([]);
  const autocompleteInstances = useRef<google.maps.places.Autocomplete[]>([]);

  useEffect(() => {
    let script: HTMLScriptElement | null = null;

    const initializeAutocompletes = () => {
      autocompleteRefs.current.forEach((input, index) => {
        if (!input || autocompleteInstances.current[index]) return;

        const autocomplete = new window.google.maps.places.Autocomplete(input, {
          types: ["establishment", "geocode"],
          fields: ["name", "formatted_address", "geometry"],
        });

        autocomplete.addListener("place_changed", () => {
          const place = autocomplete.getPlace();
          handlePlaceSelect(index, place);
        });

        autocompleteInstances.current[index] = autocomplete;
      });
    };

    if (!window.google?.maps?.places) {
      script = document.createElement("script");
      script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.GOOGLE_MAPS_API_KEY}&libraries=places`;
      script.async = true;
      script.defer = true;
      document.head.appendChild(script);
      script.onload = initializeAutocompletes;
    } else {
      initializeAutocompletes();
    }

    return () => {
      script?.remove();
      autocompleteInstances.current.forEach((instance) => {
        if (instance?.unbindAll) instance.unbindAll();
      });
    };
  }, [formData.duty_statuses.length]);

  // Ref callback for inputs
  const setAutocompleteRef = useCallback(
    (el: HTMLInputElement | null, index: number) => {
      if (el) {
        autocompleteRefs.current[index] = el;
      }
    },
    []
  );

  const handlePlaceSelect = useCallback(
    (index: number, place: google.maps.places.PlaceResult) => {
      if (!place.geometry?.location) return;

      setFormData((prev) => {
        const updatedStatuses = [...prev.duty_statuses];
        updatedStatuses[index] = {
          ...updatedStatuses[index],
          location_name: place.name || place.formatted_address || "",
          location_lat: place.geometry?.location?.lat().toString() || "",
          location_lon: place.geometry?.location?.lng().toString() || "",
        };
        return { ...prev, duty_statuses: updatedStatuses };
      });
    },
    []
  );

  const [loading, setLoading] = useState(false);

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleCheckboxChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.checked,
    }));
  };

  const addDutyStatus = () => {
    setFormData((prev) => ({
      ...prev,
      duty_statuses: [
        ...prev.duty_statuses,
        {
          status: "OFF",
          start_time: "",
          end_time: "",
          location_name: "",
          location_lat: "",
          location_lon: "",
        },
      ],
    }));
  };

  const handleDutyStatusChange = (
    index: number,
    field: string,
    value: string
  ) => {
    setFormData((prev) => {
      const updatedStatuses = prev.duty_statuses.map((ds, i) =>
        i === index ? { ...ds, [field]: value } : ds
      );
      return { ...prev, duty_statuses: updatedStatuses };
    });
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    try {
      setLoading(true);
      const formDataCopy = {
        ...formData,
        driver: formData.driver,
        vehicle: formData.vehicle,
      };

      console.log("Form data:", formDataCopy);
      

      const response = await createLog(formDataCopy);
      if (response?.id) {
        setFormData({
          date: "",
          driver: { id: "", user: { first_name: "", last_name: "" } },
          vehicle: { id: "", truck_number: "", trailer_number: "" },
          start_odometer: "",
          end_odometer: "",
          remarks: "",
          signature: "",
          adverse_conditions: false,
          duty_statuses: [],
        });

        setLoading(false);

        router.push(`/trips/${response.id}`);
      }
    } catch (error) {
      setLoading(false);
      console.error("Log creation failed:", error);
    }
  };


  return (
    <Wrapper>
      <Box p="8" style={{ maxWidth: 1200, margin: "6rem auto" }}>
        <Card variant="surface" style={{ padding: "6" }}>
          <Heading size="6" mb="4" align="center">
            Record Driver&apos;s Log Entry
          </Heading>

          <form
            onSubmit={handleSubmit}
            style={{ display: "grid", gap: "1rem", margin: "1rem" }}
          >
            <Box>
              <Text size="2" mb="1" weight="bold">
                Driver
              </Text>
              <select
                name="driver"
                value={formData.driver.id}
                onChange={handleChange}
                style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
              >
                <option value="">-- Select Driver --</option>
                {drivers.map((driver) => (
                  <option key={driver.id} value={driver.id}>
                    {driver.user?.first_name} {driver.user?.last_name}
                  </option>
                ))}
              </select>
            </Box>

            {/* Row 1: Date */}
            <Flex justify="between" wrap="wrap" gap="4">
              <Box style={{ flex: "1 1 200px" }}>
                <Text size="2" mb="1" weight="bold">
                  Date
                </Text>
                <input
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
                />
              </Box>

              <Box style={{ flex: "1 1 200px" }}>
                <Text size="2" mb="1" weight="bold">
                  Vehicle
                </Text>
                <select
                  name="vehicle"
                  value={formData.vehicle.id}
                  onChange={handleChange}
                  style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
                >
                  <option value="">-- Select Vehicle --</option>
                  {vehicles.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.truck_number} - {v.trailer_number || "No Trailer"}
                    </option>
                  ))}
                </select>
              </Box>
            </Flex>

            <Flex justify="between" wrap="wrap" gap="4">
              <Box style={{ flex: "1 1 200px" }}>
                <Text size="2" mb="1" weight="bold">
                  Start Odometer
                </Text>
                <input
                  type="number"
                  name="start_odometer"
                  placeholder="Enter start odometer"
                  value={formData.start_odometer}
                  onChange={handleChange}
                  style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
                />
              </Box>

              <Box style={{ flex: "1 1 200px" }}>
                <Text size="2" mb="1" weight="bold">
                  End Odometer
                </Text>
                <input
                  type="number"
                  name="end_odometer"
                  placeholder="Enter end odometer"
                  value={formData.end_odometer}
                  onChange={handleChange}
                  style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
                />
              </Box>
            </Flex>

            <Box>
              <Text size="2" mb="1" weight="bold">
                Signature
              </Text>
              <input
                type="text"
                name="signature"
                placeholder="Driver's signature"
                value={formData.signature}
                onChange={handleChange}
                style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
              />
            </Box>

            <Box>
              <Text size="2" mb="1" weight="bold">
                Remarks
              </Text>
              <textarea
                name="remarks"
                placeholder="Enter remarks"
                value={formData.remarks}
                onChange={handleChange}
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  fontSize: "1rem",
                  minHeight: "80px",
                }}
              />
            </Box>

            <Box>
              <label style={{ display: "flex", alignItems: "center" }}>
                <input
                  type="checkbox"
                  name="adverse_conditions"
                  checked={formData.adverse_conditions}
                  onChange={handleCheckboxChange}
                  style={{ marginRight: "0.5rem" }}
                />
                <Text size="2">Adverse Driving Conditions</Text>
              </label>
            </Box>

            <Box>
              <Text size="4" weight="bold" mb="2">
                Duty Statuses
              </Text>

              {formData.duty_statuses.map((status, index) => (
                <Card
                  key={index}
                  variant="surface"
                  mb="3"
                  style={{ display: "grid", gap: "1rem" }}
                >
                  <Flex wrap="wrap" gap="2">
                    <Box style={{ flex: "1 1 150px" }}>
                      <Text size="2" mb="1" weight="bold">
                        Status
                      </Text>
                      <select
                        value={status.status}
                        onChange={(e) =>
                          handleDutyStatusChange(
                            index,
                            "status",
                            e.target.value
                          )
                        }
                        style={{
                          width: "100%",
                          padding: "0.5rem",
                          fontSize: "1rem",
                        }}
                      >
                        <option value="OFF">Off Duty</option>
                        <option value="SB">Sleeper Berth</option>
                        <option value="D">Driving</option>
                        <option value="ON">On Duty (Not Driving)</option>
                      </select>
                    </Box>

                    <Box style={{ flex: "1 1 150px" }}>
                      <Text size="2" mb="1" weight="bold">
                        Start Time
                      </Text>
                      <input
                        type="datetime-local"
                        value={status.start_time}
                        onChange={(e) =>
                          handleDutyStatusChange(
                            index,
                            "start_time",
                            e.target.value
                          )
                        }
                        style={{
                          width: "100%",
                          padding: "0.5rem",
                          fontSize: "1rem",
                        }}
                      />
                    </Box>

                    <Box style={{ flex: "1 1 150px" }}>
                      <Text size="2" mb="1" weight="bold">
                        End Time
                      </Text>
                      <input
                        type="datetime-local"
                        value={status.end_time}
                        onChange={(e) =>
                          handleDutyStatusChange(
                            index,
                            "end_time",
                            e.target.value
                          )
                        }
                        style={{
                          width: "100%",
                          padding: "0.5rem",
                          fontSize: "1rem",
                        }}
                      />
                    </Box>

                    <Box style={{ flex: "1 1 300px" }}>
                      <Text size="2" mb="1" weight="bold">
                        Location
                      </Text>
                      <input
                        placeholder="Type location"
                        ref={(el) => setAutocompleteRef(el, index)}
                        defaultValue={status.location_name}
                        style={{ width: "100%", padding: "0.5rem" }}
                      />
                    </Box>
                  </Flex>
                </Card>
              ))}

              <Button
                onClick={addDutyStatus}
                variant="soft"
                color="gray"
                size="2"
                type="button"
              >
                Add Duty Status
              </Button>
            </Box>

            <Button
              type="submit"
              size="4"
              color="gray"
              variant="solid"
              highContrast
              style={{ marginTop: "1rem" }}
              disabled={loading}
            >
              Submit Log Entry
            </Button>
          </form>
        </Card>
      </Box>
    </Wrapper>
  );
}
