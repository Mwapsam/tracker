const BASE_URL = "https://test.taskcentro.com";

export { BASE_URL };

export interface Carrier {
  name: string;
  mc_number: string;
  main_office_address: string;
  home_terminal_address: string;
  hos_cycle_choice: string;
}

export interface DutyStatus {
  id: string;
  status: string;
  status_display: string;
  start_time: string;
  end_time: string;
  location: {
    lat: number | null;
    lon: number | null;
    name: string;
  };
}

export interface Driver {
  id?: string
  user?: {
    first_name: string;
    last_name: string;
    email?: string;
  };
  license_number?: string;
  current_cycle_used?: string;
  last_34hr_restart?: string;
  carrier?: Carrier;
}

export interface Vehicle {
  id?: string;
  truck_number?: string;
  trailer_number?: string;
}

export interface LogEntry {
  id: number;
  date: string;
  start_odometer: number;
  end_odometer: number;
  remarks: string;
  signature: string;
  duty_statuses: DutyStatus[];
  driver: Driver;
  vehicle: Vehicle;
  total_miles: string;
  adverse_conditions: string;
}

export interface DutyStatusInput {
  status: string;
  start_time: string;
  end_time: string;
  location_name: string;
  location_lat: string;
  location_lon: string;
}

export interface LogEntryFormData {
  date: string;
  vehicle: Vehicle;
  driver: Driver;
  start_odometer: string;
  end_odometer: string;
  remarks: string;
  signature: string;
  adverse_conditions: boolean;
  duty_statuses: DutyStatusInput[];
}
