export interface Turbine {
	wt_id: string
	generator_temp: number
	rotor_rps: number
	tower_vib_freq: number
}

export interface Coord {
	lat: number
	lng: number
}

export interface Boundaries {
	north: number
	south: number
	east: number
	west: number
}

type Drone = { id: string } & Coord

export interface Map {
	area: Coord[]
	boundaries: Boundaries
	center: Coord
	defaultZoom: number
	minZoom: number
	turbines: Array<{ id: string } & Coord>
	drones: Drone[]
}

export interface Env {
	env_temp: number
	env_wind_angle: number
	env_wind_mag: number
	wave_mag: number
	visibility: number
}
