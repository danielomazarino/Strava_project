module.exports = {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				ink: '#1c1a17',
				slate: '#54504a',
				sand: '#f5efe5',
				paper: '#fffaf3',
				ember: '#e06b2f',
				pine: '#245c4a',
				steel: '#6c7a86'
			},
			boxShadow: {
				soft: '0 28px 80px rgba(17, 15, 12, 0.14)',
				glow: '0 0 0 1px rgba(211, 101, 40, 0.22), 0 18px 42px rgba(211, 101, 40, 0.16)'
			},
			fontFamily: {
				sans: ['"Inter"', 'ui-sans-serif', 'system-ui'],
				display: ['"Inter Tight"', '"Inter"', 'ui-sans-serif', 'system-ui']
			}
		}
	},
	plugins: [require('@tailwindcss/typography')]
};