import { addExcludeAnnouncementsListeners } from "./exclude_announcements_listeners.js";
import { addCreateRowListener } from "./create_row_listener.js";
import { addAdditionalEnrollmentsObserver } from "./additional_enrollments_observer.js";
import { addEnterKeyListener } from "./enter_key_listener.js";

addExcludeAnnouncementsListeners();
addCreateRowListener("id_add_enrollment");
addAdditionalEnrollmentsObserver();
addEnterKeyListener();
