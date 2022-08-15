import { getRowValues } from "./user_row.js";

export function handleLoadOrEditButton(button, includeSchoolAndSubject) {
  if (!button) {
    return;
  }
  button.addEventListener("click", (event) => getRowValues(event.target, includeSchoolAndSubject));
}
