export type TurbineStatus = 'running' | 'warning' | 'failure' | 'idle'

export type DroneStatus = 'travelling' | 'warning' | 'failure' | 'idle'

export interface Turbine {
	wt_id: string
	status: TurbineStatus
	generator_temp: number
	tower_vib_freq: number
	rotor_rps: number[]
	power: number[]
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

export type Drone = {
	drone_id: string
	status: DroneStatus
} & Coord

type Station = { id: string } & Coord

export interface Map {
	area: Coord[]
	boundaries: Boundaries
	center: Coord
	defaultZoom: number
	minZoom: number
	turbines: Array<{ id: string } & Coord>
	drones: Drone[]
	stations: Station[]
}

export interface Env {
	env_temp: number
	env_wind_angle: number
	env_wind_mag: number
	wave_mag: number
	visibility: number
}
