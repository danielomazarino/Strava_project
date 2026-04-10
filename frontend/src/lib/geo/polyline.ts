export type GeoPoint = {
	lat: number;
	lng: number;
};

export type PolylinePreview = {
	path: string;
	width: number;
	height: number;
	padding: number;
	points: GeoPoint[];
};

export function decodePolyline(encoded: string): GeoPoint[] {
	const points: GeoPoint[] = [];
	let index = 0;
	let lat = 0;
	let lng = 0;

	while (index < encoded.length) {
		let shift = 0;
		let result = 0;
		let byte: number;

		do {
			byte = encoded.charCodeAt(index++) - 63;
			result |= (byte & 0x1f) << shift;
			shift += 5;
		} while (byte >= 0x20);

		const deltaLat = result & 1 ? ~(result >> 1) : result >> 1;
		lat += deltaLat;

		shift = 0;
		result = 0;

		do {
			byte = encoded.charCodeAt(index++) - 63;
			result |= (byte & 0x1f) << shift;
			shift += 5;
		} while (byte >= 0x20);

		const deltaLng = result & 1 ? ~(result >> 1) : result >> 1;
		lng += deltaLng;

		points.push({ lat: lat / 1e5, lng: lng / 1e5 });
	}

	return points;
}

export function buildPolylinePreview(points: GeoPoint[], width = 640, height = 320, padding = 28): PolylinePreview | null {
	if (points.length === 0) {
		return null;
	}

	const minLat = Math.min(...points.map((point) => point.lat));
	const maxLat = Math.max(...points.map((point) => point.lat));
	const minLng = Math.min(...points.map((point) => point.lng));
	const maxLng = Math.max(...points.map((point) => point.lng));

	const latSpan = Math.max(maxLat - minLat, 0.0001);
	const lngSpan = Math.max(maxLng - minLng, 0.0001);
	const drawableWidth = width - padding * 2;
	const drawableHeight = height - padding * 2;

	const scaledPoints = points.map((point) => {
		const x = padding + ((point.lng - minLng) / lngSpan) * drawableWidth;
		const y = height - padding - ((point.lat - minLat) / latSpan) * drawableHeight;
		return { x, y };
	});

	const path = scaledPoints
		.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`)
		.join(' ');

	return {
		path,
		width,
		height,
		padding,
		points
	};
}