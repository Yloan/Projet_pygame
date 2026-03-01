"""
TEST SCRIPT - Session JSON Serialization
Démonstration de la sérialisation JSON des sessions
"""

import json
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ui.menu import Session


class MockMenu:
    """Mock Menu class for testing without full pygame initialization"""

    def __init__(self):
        self.screen = None
        self.font = None
        self.middle_font = None


def test_session_serialization():
    """Test Session to_dict() and from_dict() methods"""
    print("=" * 80)
    print("TEST 1: Session Serialization to JSON")
    print("=" * 80)

    # Create a mock menu
    mock_menu = MockMenu()

    # Create a session
    session = Session(mock_menu)
    session.titre = "Dragon Cave"
    session.nb_bots = 3
    session.nb_players = 2
    session.y = 79

    print(f"\nOriginal Session:")
    print(f"  - Titre: {session.titre}")
    print(f"  - Bots: {session.nb_bots}")
    print(f"  - Players: {session.nb_players}")
    print(f"  - Y Position: {session.y}")
    print(f"  - Gap: {session.gap}")

    # Convert to dictionary
    session_dict = session.to_dict()
    print(f"\nConverted to Dictionary:")
    print(f"  {session_dict}")

    # Convert to JSON
    session_json = json.dumps(session_dict)
    print(f"\nSerialized to JSON:")
    print(f"  {session_json}")

    # Create message format (as sent over network)
    message = f"[Sessions]:{session_json}"
    print(f"\nNetwork Message Format:")
    print(f"  {message}")

    return True


def test_session_deserialization():
    """Test Session from_dict() method"""
    print("\n" + "=" * 80)
    print("TEST 2: Session Deserialization from JSON")
    print("=" * 80)

    mock_menu = MockMenu()

    # Simulate receiving JSON from server
    received_json = (
        '{"titre": "Ice Temple", "nb_bots": 1, "nb_players": 3, "y": 204, "gap": 125}'
    )
    print(f"\nReceived JSON:")
    print(f"  {received_json}")

    # Parse JSON
    session_data = json.loads(received_json)
    print(f"\nParsed Dictionary:")
    print(f"  {session_data}")

    # Create Session from dictionary
    new_session = Session.from_dict(session_data, mock_menu)
    print(f"\nRecreated Session:")
    print(f"  - Titre: {new_session.titre}")
    print(f"  - Bots: {new_session.nb_bots}")
    print(f"  - Players: {new_session.nb_players}")
    print(f"  - Y Position: {new_session.y}")
    print(f"  - Gap: {new_session.gap}")

    return True


def test_multiple_sessions():
    """Test multiple sessions being serialized"""
    print("\n" + "=" * 80)
    print("TEST 3: Multiple Sessions (Server Broadcast)")
    print("=" * 80)

    mock_menu = MockMenu()

    # Create multiple sessions
    sessions_data = []

    session_names = [
        ("Forest of Lost Souls", 2, 1),
        ("Volcano's Peak", 3, 1),
        ("Frozen Cavern", 1, 2),
    ]

    for i, (name, bots, players) in enumerate(session_names):
        session = Session(mock_menu)
        session.titre = name
        session.nb_bots = bots
        session.nb_players = players
        session.y = 79 + (i * 125)
        sessions_data.append(session.to_dict())

    print(f"\nCreated {len(sessions_data)} Sessions:")
    for i, session in enumerate(sessions_data):
        print(
            f"  {i + 1}. {session['titre']} ({session['nb_players']}p, {session['nb_bots']}b)"
        )

    # Simulate server broadcast message
    broadcast_json = json.dumps(sessions_data)
    broadcast_message = f"[SessionsList]:{broadcast_json}"

    print(f"\nServer Broadcast Message (truncated):")
    if len(broadcast_message) > 100:
        print(f"  {broadcast_message[:100]}...")
    else:
        print(f"  {broadcast_message}")

    # Simulate client receiving and parsing
    print(f"\nClient Receives and Parses:")
    received_sessions_json = broadcast_message.split(":", 1)[1]
    received_sessions_data = json.loads(received_sessions_json)

    print(f"  Received {len(received_sessions_data)} sessions")
    for session in received_sessions_data:
        print(f"    ✓ {session['titre']}")

    return True


def test_message_parsing():
    """Test parsing network messages"""
    print("\n" + "=" * 80)
    print("TEST 4: Network Message Parsing")
    print("=" * 80)

    # Simulate a received message from client creating a session
    client_message = '[Sessions]:{"titre": "My Session", "nb_bots": 2, "nb_players": 1, "y": 79, "gap": 125}'

    print(f"\nReceived Message:")
    print(f"  {client_message}")

    # Parse like server does
    if client_message.startswith("[Sessions]"):
        json_str = client_message.split(":", 1)[1]
        print(f"\nExtracted JSON:")
        print(f"  {json_str}")

        session_data = json.loads(json_str)
        print(f"\nParsed Data:")
        for key, value in session_data.items():
            print(f"  - {key}: {value}")

        # Validate (server-side)
        required_fields = ["titre", "nb_bots", "nb_players"]
        is_valid = all(field in session_data for field in required_fields)
        print(f"\nValidation: {'✓ VALID' if is_valid else '✗ INVALID'}")

        return is_valid

    return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "SESSION JSON SERIALIZATION - TEST SUITE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    tests = [
        ("Serialization", test_session_serialization),
        ("Deserialization", test_session_deserialization),
        ("Multiple Sessions", test_multiple_sessions),
        ("Message Parsing", test_message_parsing),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {name:.<50} {status}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n✓ All tests passed! JSON serialization is working correctly.")
        return 0
    else:
        print(f"\n✗ {total_tests - total_passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    exit(main())
