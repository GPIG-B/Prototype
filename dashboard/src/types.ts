export type DeviceStatus = 'running' | 'warning' | 'failure' | 'idle'

export interface Turbine {
	wt_id: string
	status: DeviceStatus
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

export type Drone = { drone_id: string } & Coord

type Station = { id: string } & Coord

export interface Map {
	area: Coord[]
	boundaries: Boundaries
	center: Coord
	defaultZoom: number
	minZoom: number
	turbines: Array<{ id: string } & Coord>
	drones: Array<{ id: string } & Coord>
	stations: Station[]
}

export interface Env {
	env_temp: number
	env_wind_angle: number
	env_wind_mag: number
	wave_mag: number
	visibility: number
}
