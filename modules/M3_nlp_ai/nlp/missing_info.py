class MissingInfoDetector:
    """Find only core fields needed for eligibility, prioritized for best UX."""

    # Prioritized order as per SchemeMitra specification:
    # 1. age
    # 2. state/location
    # 3. business/activity
    # 4. education
    # 5. category
    # 6. income
    # 7. project cost / capital
    REQUIRED_FIELDS = [
        "age", "gender", "state", "sector", "business_type", "education",
        "category", "income", "project_cost",
    ]

    FIELD_QUESTIONS = {
        "age": "What is your age?",
        "gender": "What is your gender?",
        "state": "Which state do you live in?",
        "sector": "What type of business or activity are you planning or running?",
        "business_type": "Is this a new business idea/startup or an existing running business?",
        "education": "What is your highest level of education qualification?",
        "category": "What is your social category (e.g., SC, ST, OBC, General, or EWS)?",
        "income": "What is your approximate annual family income?",
        "project_cost": "What is the estimated cost or budget for your project?",
    }

    def find_missing(self, profile):
        if not isinstance(profile, dict):
            raise TypeError("Profile must be a dictionary.")
        return [f for f in self.REQUIRED_FIELDS if f not in profile or profile[f] is None]

    def get_questions(self, missing_fields, profile=None):
        if not isinstance(missing_fields, list):
            raise TypeError("Missing fields must be a list.")
        
        questions = []
        profile = profile or {}

        # 1. Education Field Ambiguity Clarification
        if profile.get("education_field") and not profile.get("education"):
            field_name = profile["education_field"]
            questions.append(
                f"What qualification did you complete in {field_name}? For example, B.E., B.Tech, B.Sc., BCA, M.Sc., M.Tech or MCA."
            )

        # 2. Location State Ambiguity Clarification
        if profile.get("district") and not profile.get("state"):
            questions.append(
                f"Which state is {profile['district']} located in?"
            )

        for f in missing_fields:
            if f == "education" and profile.get("education_field") and not profile.get("education"):
                # Already added specific qualification clarification above
                continue
            if f == "state" and profile.get("district") and not profile.get("state"):
                # Already added specific state clarification above
                continue
            if f in self.FIELD_QUESTIONS:
                questions.append(self.FIELD_QUESTIONS[f])

        return questions

    def analyze(self, profile):
        missing = self.find_missing(profile)
        questions = self.get_questions(missing, profile)
        return {"missing_fields": missing, "questions": questions, "complete": not missing}

