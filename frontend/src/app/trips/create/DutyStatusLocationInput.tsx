import { usePlacesWidget } from "react-google-autocomplete";

type DutyStatusLocationInputProps = {
  index: number;
  locationName: string;
  handlePlaceSelect: (
    index: number,
    place: google.maps.places.PlaceResult
  ) => void;
};

export default function DutyStatusLocationInput({
  index,
  handlePlaceSelect,
  locationName,
}: DutyStatusLocationInputProps) {
  const { ref } = usePlacesWidget({
    apiKey: process.env.GOOGLE_MAPS_API_KEY,
    onPlaceSelected: (place) => {
      console.log("Hook place selection:", place);
      handlePlaceSelect(index, place);
    },
    options: {
      types: ["establishment", "geocode"],
      fields: ["name", "formatted_address", "geometry"],
    },
  });


  return (
    <input
      ref={ref}
      className="autocomplete-input"
      style={{
        width: "100%",
        padding: "0.5rem",
        fontSize: "1rem",
        border: "1px solid #ccc",
      }}
      defaultValue={locationName}
    />
  );
}
