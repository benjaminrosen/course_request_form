import { getEnrollmentUserValues } from "./enrollment_user.js";

export function handleLoadOrEditButton(button) {
  if (!button) {
    return;
  }
  button.addEventListener("click", (event) =>
    getEnrollmentUserValues(event.target)
  );
}
