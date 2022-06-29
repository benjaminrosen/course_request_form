function loadUser(target) {
  const enrollmentCount = getEnrollmentCount();
  const { pennkey, role } = getPennkeyAndRole(target);
  const hxVals = JSON.stringify({ enrollmentCount, pennkey, role });
  target.setAttribute("hx-vals", hxVals);
  console.log(target);
}

function addButtonListener() {
  const button = document.getElementById(
    "load_user_{{ new_enrollment_count }}"
  );
  button.addEventListener("click", (event) => {
    loadUser(event.target);
  });
}

addButtonListener();
