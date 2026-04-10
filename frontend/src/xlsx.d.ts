declare module 'xlsx' {
	export const utils: {
		book_new: () => unknown;
		json_to_sheet: (rows: Record<string, string>[]) => unknown;
		book_append_sheet: (workbook: unknown, worksheet: unknown, name: string) => void;
	};

	export const writeFile: (workbook: unknown, filename: string) => void;
}