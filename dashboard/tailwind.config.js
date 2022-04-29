const plugin = require('tailwindcss/plugin')

module.exports = {
	content: [
		'./src/pages/**/*.{js,ts,jsx,tsx}',
		'./src/components/**/*.{js,ts,jsx,tsx}',
		'./src/config/**/*.{js,ts}',
	],
	theme: {
		extend: {
			colors: {
				'blue-gray-100': '#DCE6FF',
				'blue-gray-400': '#8F99CC',
				'blue-gray-600': '#646FA7',
				'blue-100': '#E9EEFD',
				'blue-400': '#C8D3F6',
				'blue-600': '#3661ED',
				'red-100': '#FFE7E4',
				'red-600': '#FC5C4C',
				'yellow-100': '#FFF4E3',
				'yellow-600': '#FBB34C',
				'green-400': '#E3FFEA',
				'green-600': '#4CFB73',
				'gray-200': '#EFEFEF',
				'gray-100': '#D9D9D9',
				'gray-600': '#404040',
			},
		},
	},
	plugins: [
		plugin(function ({ addUtilities, matchUtilities, theme }) {
			// Add default utilities for border-spacing
			addUtilities({
				'.border-spacing-2': {
					'border-spacing': '0.5rem',
				},
				'.border-spacing-4': {
					'border-spacing': '1rem',
				},
			})

			// Add dynamic match for arbitrary values (e.g. border-spacing-[50px])
			matchUtilities(
				{
					'border-spacing': (value) => ({
						'border-spacing': value,
					}),
				},
				{ values: theme('borderSpacing') }
			)
		}),
	],
}
