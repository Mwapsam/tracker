import { Vehicle } from "@/utils";
import { DashboardIcon, PlusIcon, RocketIcon } from "@radix-ui/react-icons";
import {
  Badge,
  Box,
  Button,
  Dialog,
  Flex,
  Heading,
  Text,
} from "@radix-ui/themes";
import React from "react";
import GooglePlacesAutocomplete from "react-google-places-autocomplete";

type Props = {
  showTripForm: boolean;
  setShowTripForm: React.Dispatch<React.SetStateAction<boolean>>;
  isTripActive: boolean;
  handleCreateTrip: () => Promise<void>;
  vehicles: Vehicle[];
  isCreatingTrip: boolean;

  formData: {
    current_location: string;
    pickup_location: string;
    dropoff_location: string;
    current_cycle_used: number;
    vehicle: string;
    driver: string;
  };
  handleInputChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => void;
  setFormData: React.Dispatch<
    React.SetStateAction<{
      current_location: string;
      pickup_location: string;
      dropoff_location: string;
      current_cycle_used: number;
      vehicle: string;
      driver: string;
    }>
  >;
};

const TopBox: React.FC<Props> = ({
  showTripForm,
  setShowTripForm,
  isTripActive,
  formData,
  handleInputChange,
  setFormData,
  handleCreateTrip,
  isCreatingTrip,
  vehicles,
}) => {
  return (
    <Flex justify="between" align="center" mb="5">
      <Flex align="center" gap="4">
        <DashboardIcon width={32} height={32} />
        <Heading size="7" weight="bold">
          Driver Dashboard
        </Heading>
      </Flex>

      <Flex gap="3" align="center">
        <Dialog.Root open={showTripForm} onOpenChange={setShowTripForm}>
          <Dialog.Trigger>
            <Button variant="soft" disabled={isTripActive}>
              <PlusIcon /> New Trip
            </Button>
          </Dialog.Trigger>

          <Dialog.Content style={{ maxWidth: 550 }}>
            <Dialog.Title>Create New Trip</Dialog.Title>
            <Dialog.Description mb="4">
              Enter trip details to begin tracking
            </Dialog.Description>

            <Flex direction="column" gap="5">
              <label>
                <Text as="div" size="2" mb="1" weight="bold">
                  Current Location
                </Text>
                <input
                  name="current_location"
                  value={formData.current_location}
                  onChange={handleInputChange}
                  placeholder="Enter current location"
                  className="custom-input"
                  disabled
                />
              </label>
              <label>
                <Text as="div" size="2" mb="1" weight="bold">
                  Pickup Location
                </Text>
                <GooglePlacesAutocomplete
                  selectProps={{
                    value:
                      typeof formData.pickup_location === "string"
                        ? {
                            label: formData.pickup_location,
                            value: formData.pickup_location,
                          }
                        : formData.pickup_location,
                    onChange: (value) =>
                      setFormData((prev) => ({
                        ...prev,
                        pickup_location: value
                          ? typeof value === "string"
                            ? value
                            : value.label
                          : "",
                      })),
                  }}
                />
              </label>
              <label>
                <Text as="div" size="2" mb="1" weight="bold">
                  Dropoff Location
                </Text>
                <GooglePlacesAutocomplete
                  selectProps={{
                    value:
                      typeof formData.dropoff_location === "string"
                        ? {
                            label: formData.dropoff_location,
                            value: formData.dropoff_location,
                          }
                        : formData.dropoff_location,

                    onChange: (value) =>
                      setFormData((prev) => ({
                        ...prev,
                        dropoff_location: value
                          ? typeof value === "string"
                            ? value
                            : value.label
                          : "",
                      })),
                  }}
                />
              </label>
              <label>
                <Text as="div" size="2" mb="1" weight="bold">
                  Current Cycle Used (Hrs)
                </Text>
                <input
                  name="current_cycle_used"
                  value={formData.current_cycle_used}
                  onChange={handleInputChange}
                  placeholder="Enter hours used"
                  className="custom-input"
                  type="number"
                  disabled
                />
              </label>
              <Box style={{ flex: "1 1 20px" }}>
                <Text size="2" mb="1" weight="bold">
                  Vehicle
                </Text>
                <select
                  name="vehicle"
                  value={formData.vehicle}
                  onChange={handleInputChange}
                  style={{
                    width: "100%",
                    padding: "0.5rem",
                    fontSize: "1rem",
                  }}
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

            <Flex gap="3" mt="4" justify="end">
              <Dialog.Close>
                <Button variant="soft" color="gray">
                  Cancel
                </Button>
              </Dialog.Close>
              <Button onClick={handleCreateTrip} disabled={isCreatingTrip}>
                <RocketIcon /> {isCreatingTrip ? "Creating..." : "Start Trip"}
              </Button>
            </Flex>
          </Dialog.Content>
        </Dialog.Root>

        <Badge
          color={isTripActive ? "green" : "gray"}
          radius="full"
          size="2"
          variant="soft"
        >
          <Flex gap="2" align="center">
            <Box
              style={{
                width: "8px",
                height: "8px",
                background: `var(--${isTripActive ? "green" : "gray"}-9)`,
                borderRadius: "50%",
              }}
            />
            {isTripActive ? "Active - 70h/8d" : "No Active Trip"}
          </Flex>
        </Badge>
      </Flex>
    </Flex>
  );
};

export default TopBox;
