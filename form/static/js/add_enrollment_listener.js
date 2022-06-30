import { getEnrollmentCount } from "./enrollment_count.js";

export function addAddEnrollmentListener() {
  const addEnrollment = document.getElementById("id_add_enrollment");
  addEnrollment.addEventListener("click", (event) => {
    const enrollmentCount = getEnrollmentCount();
    const hxVals = JSON.stringify({ enrollmentCount });
    event.target.setAttribute("hx-vals", hxVals);
  });
}
