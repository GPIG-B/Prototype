import { TurbineStatus, DroneStatus, LogLevel } from '@/types'

export const turbineStatuses: TurbineStatus[] = [
	'running',
	'warning',
	'failure',
	'idle',
]

export const droneStatuses: DroneStatus[] = [
	'travelling',
	'warning',
	'failure',
	'idle',
]

export const statusThemes: Record<
	TurbineStatus | DroneStatus,
	{ background: string; text: string }
> = {
	running: {
		background: 'bg-blue-600',
		text: 'text-blue-600',
	},
	travelling: {
		background: 'bg-blue-600',
		text: 'text-blue-600',
	},
	warning: {
		background: 'bg-yellow-600',
		text: 'text-yellow-600',
	},
	failure: {
		background: 'bg-red-600',
		text: 'text-red-600',
	},
	idle: {
		background: 'bg-gray-600',
		text: 'text-gray-600',
	},
}

export const logStatuses: LogLevel[] = ['info', 'warning', 'failure']

export const maxTurbineFrequency = 8000

export const minDangerTurbineFrequency = 6000

export const minWarningTurbineFrequency = 4400

export const maxTurbineTemperature = 100

export const minDangerTurbineTemperature = 50

export const minWarningTurbineTemperature = 25
