# TODO: ADD Documentation

# SECTION: External dependencies
import sys

# SECTION: Internal dependencies
from census.fips import update_fips_codes


def main():
    print("Running pre-commit hooks, thank you for your patience")

    # --- updating FIPS codes
    print("Updating FIPS codes")

    # update_fips_codes will throw if:
    # 1. Contributor does not have an "api_keys.env" file in the right place
    # 2. They choose not to continue when prompted
    try:
        update_fips_codes()
    except ValueError:
        print("Stopping Commit!")
        sys.exit(1)

    # successful if reached this point
    print("Thank you for your patience and contribution!")
    sys.exit(0)


if __name__ == "__main__":
    main()
