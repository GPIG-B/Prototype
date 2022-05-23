import axios, { AxiosRequestConfig } from 'axios'
import useSWR, { SWRConfiguration, SWRResponse } from 'swr'

const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/*$/, '')

const _timeout = process.env.NEXT_PUBLIC_API_TIMEOUT
const timeout = (_timeout && parseInt(_timeout)) || 10 * 1000

const fetchApi = axios.create({
	baseURL,
	timeout,
	// withCredentials: true,
})

type Fetch = <T>(
	url: string,
	options?: AxiosRequestConfig
) => Promise<{ data: T; error: null } | { error: string; data: null }>

export const fetch: Fetch = async (url, options = {}) => {
	try {
		const { data } = await fetchApi(url, options)
		return { data, error: null }
	} catch (e) {
		const error = (e as any)?.message || 'An unexpected error occurred'
		return { error, data: null }
	}
}

type UseSwr = <T = any, K = any>(
	url: string | null,
	options?: SWRConfiguration
) => SWRResponse<T, K>

const swrDefaults: SWRConfiguration = {
	onErrorRetry: (error, _key, _config, revalidate, { retryCount }) => {
		// Never retry on 401 or 404
		if (error.status === 401 || error.status === 404) return

		// Only retry up to 10 times
		if (retryCount >= 5) return

		// Retry after 5 seconds
		setTimeout(() => revalidate({ retryCount }), 10000)
	},
	errorRetryCount: 5,
}

const swrFetch = async (url: string) => {
	const { data } = await fetchApi.get(url)
	return data
}

export const useSwr: UseSwr = (url, options = {}) => {
	const useSwrOptions = { ...swrDefaults, ...options }
	return useSWR(url, swrFetch, useSwrOptions)
}
