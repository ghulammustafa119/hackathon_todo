/**
 * Safely extract a string error message from any error shape.
 * Handles: FastAPI validation errors, Better Auth errors, plain strings, Error objects.
 */
export function extractErrorMessage(error: any): string {
  if (!error) return "Something went wrong";

  // Already a string
  if (typeof error === "string") return error;

  // FastAPI single validation error object: { type, loc, msg, input, ctx }
  if (error.msg && typeof error.msg === "string") return error.msg;

  // Standard Error or { message: "..." }
  if (error.message && typeof error.message === "string") return error.message;

  // FastAPI detail as string: { detail: "Some error" }
  if (typeof error.detail === "string") return error.detail;

  // FastAPI detail as array: { detail: [{ type, loc, msg, input, ctx }, ...] }
  if (Array.isArray(error.detail) && error.detail.length > 0) {
    return error.detail
      .map((e: any) => (typeof e === "string" ? e : e.msg || "Error"))
      .join(", ");
  }

  // Array of error objects directly
  if (Array.isArray(error) && error.length > 0) {
    return error
      .map((e: any) => (typeof e === "string" ? e : e.msg || "Error"))
      .join(", ");
  }

  return "Something went wrong";
}
