from .support_inference import SupportInference


class ProfileValidator:
    """Validate M3 data quality. This is not an eligibility engine."""

    ALLOWED_GENDERS = {"Male", "Female", "Transgender"}
    ALLOWED_CATEGORIES = {"SC", "ST", "OBC", "General", "EWS"}
    ALLOWED_EDUCATION = {"8th_pass", "10th_pass", "12th_pass", "Diploma", "ITI", "Degree", "Postgraduate", "PhD", "School", "Graduate", "10th", "12th"}
    ALLOWED_BUSINESS_TYPES = {"Startup", "Existing", "Idea"}
    ALLOWED_SECTORS = {
        "Food", "Food Processing", "Manufacturing", "Service", "Handicrafts", "Textile", "Textiles",
        "Agriculture", "Dairy", "Fisheries", "Technology", "Retail", "Education", "Healthcare",
        "Food Processing & Agri Value Addition", "Agriculture & Allied", "MSME & Manufacturing",
        "Finance & Credit", "Startup & Innovation", "Skills & Employment",
        "Women & SHG Entrepreneurship", "Social Empowerment & Inclusive Entrepreneurship",
        "Handicrafts, Handloom & Artisan Economy", "Export, Market Access & Business Growth",
    }
    ALLOWED_BUSINESS_GOALS = {"START_BUSINESS", "GROW_BUSINESS"}

    def validate(self, profile):
        if not isinstance(profile, dict):
            raise TypeError("Profile must be a dictionary.")
        errors = []

        if "age" in profile:
            age = profile["age"]
            if not isinstance(age, int):
                errors.append("Age must be an integer.")
            elif age < 1 or age > 120:
                errors.append("Age must be between 1 and 120.")

        if "gender" in profile and profile["gender"] not in self.ALLOWED_GENDERS:
            errors.append(f"Invalid gender: {profile['gender']}")
        if "state" in profile and (not isinstance(profile["state"], str) or not profile["state"].strip()):
            errors.append("State must be a non-empty string.")
        if "education" in profile and profile["education"] not in self.ALLOWED_EDUCATION:
            errors.append(f"Invalid education: {profile['education']}")
        if "category" in profile and profile["category"] not in self.ALLOWED_CATEGORIES:
            errors.append(f"Invalid category: {profile['category']}")
        if "business_type" in profile and profile["business_type"] not in self.ALLOWED_BUSINESS_TYPES:
            errors.append(f"Invalid business type: {profile['business_type']}")
        if "sector" in profile and profile["sector"] not in self.ALLOWED_SECTORS:
            errors.append(f"Invalid sector: {profile['sector']}")

        for field, label in (("income", "Income"), ("project_cost", "Project cost"), ("available_capital", "Available capital")):
            if field in profile:
                value = profile[field]
                if not isinstance(value, (int, float)):
                    errors.append(f"{label} must be numeric.")
                elif value < 0:
                    errors.append(f"{label} cannot be negative.")

        if "new_business" in profile and not isinstance(profile["new_business"], bool):
            errors.append("new_business must be True or False.")
        if "artisan_trade" in profile and not isinstance(profile["artisan_trade"], str):
            errors.append("artisan_trade must be a string.")
        if "business_goal" in profile and profile["business_goal"] not in self.ALLOWED_BUSINESS_GOALS:
            errors.append(f"Invalid business goal: {profile['business_goal']}")

        for field in ("preferred_support_types", "support_needs"):
            if field in profile:
                value = profile[field]
                if not isinstance(value, list):
                    errors.append(f"{field} must be a list.")
                else:
                    invalid = [x for x in value if x not in SupportInference.SUPPORT_TYPES]
                    if invalid:
                        errors.append(f"Invalid {field}: {invalid}")

        recommended = ["age", "gender", "state", "education", "category", "business_type", "sector", "income", "project_cost"]
        missing = [f for f in recommended if f not in profile]
        return {"valid": not errors, "errors": errors, "missing_fields": missing, "profile": profile}
