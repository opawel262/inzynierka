from fastapi import status


register_response = {
    status.HTTP_201_CREATED: {
        "description": "User created successfully, activation email sent",
        "content": {
            "application/json": {
                "examples": {
                    "success": {
                        "summary": "Successful Registration",
                        "value": {
                            "detail": "Proszę sprawdzić swój email, aby aktywować konto"
                        },
                    }
                }
            }
        },
    },
    status.HTTP_400_BAD_REQUEST: {
        "description": "Validation errors",
        "content": {
            "application/json": {
                "examples": {
                    "email_exists": {
                        "summary": "Email Already Registered",
                        "value": {"detail": "Ten adres email jest już zarejestrowany"},
                    },
                    "password_too_short": {
                        "summary": "Password Too Short",
                        "value": {"detail": "Hasło musi mieć co najmniej 12 znaków"},
                    },
                    "missing_digit": {
                        "summary": "Password Missing Digit",
                        "value": {
                            "detail": "Hasło musi zawierać co najmniej jedną cyfrę"
                        },
                    },
                    "missing_uppercase": {
                        "summary": "Password Missing Uppercase Letter",
                        "value": {
                            "detail": "Hasło musi zawierać co najmniej jedną wielką literę"
                        },
                    },
                    "missing_lowercase": {
                        "summary": "Password Missing Lowercase Letter",
                        "value": {
                            "detail": "Hasło musi zawierać co najmniej jedną małą literę"
                        },
                    },
                    "missing_special_char": {
                        "summary": "Password Missing Special Character",
                        "value": {
                            "detail": "Hasło musi zawierać co najmniej jeden znak specjalny"
                        },
                    },
                    "invalid_email_format": {
                        "summary": "Invalid Email Format",
                        "value": {
                            "detail": "Niepoprawny format adresu email"
                        },
                    },
                }
            }
        },
    },
}
