export type DeviceStatus = 'running' | 'warning' | 'failure' | 'idle'

export const deviceStatuses = ['running', 'warning', 'failure', 'idle']

export const statusThemes: Record<
	DeviceStatus,
	{ background: string; text: string }
> = {
	running: {
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

export type LogStatus = 'failure' | 'warning' | 'info'

export const logStatuses = ['failure', 'warning', 'info']

export const maxTurbineFrequency = 200

export const minDangerTurbineFrequency = 120

export const minWarningTurbineFrequency = 80

export const maxTurbineTemperature = 120

export const minDangerTurbineTemperature = 80

export const minWarningTurbineTemperature = 50
