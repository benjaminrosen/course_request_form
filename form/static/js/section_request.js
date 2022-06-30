import { addExcludeAnnouncementsListeners } from "./exclude_announcements_listeners.js";
import {
  getEnrollmentCount,
  getElementByEnrollmentCount,
} from "./enrollment_count.js";
import { addAddEnrollmentListener } from "./add_enrollment_listener.js";
import { addAdditionalEnrollmentsObserver } from "./additional_enrollments_observer.js";
import { addEnterKeyListener } from "./enter_key_listener.js";

addExcludeAnnouncementsListeners();
addAddEnrollmentListener();
addAdditionalEnrollmentsObserver();
addEnterKeyListener();
