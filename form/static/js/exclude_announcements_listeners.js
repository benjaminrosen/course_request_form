function setExcludeAnnouncementsDisplay(displayValue) {
  const excludeAnnouncements = document.getElementById(
    "id_exclude_announcements"
  );
  excludeAnnouncements.style.display = displayValue;
}

export function addExcludeAnnouncementsListeners() {
  const proxyRequester = document.getElementById("id_proxy_requester");
  if (proxyRequester) {
    proxyRequester.addEventListener("change", (event) =>
      setExcludeAnnouncementsDisplay("none")
    );
  }
  const copyFromCourse = document.getElementById("id_copy_from_course");
  if (copyFromCourse) {
    copyFromCourse.addEventListener("change", (event) =>
      setExcludeAnnouncementsDisplay("block")
    );
  }
}
