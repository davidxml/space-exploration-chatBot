import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables (API Keys)
load_dotenv()

# --- CONFIGURATION ---
TARGET_PAIRS_PER_TOPIC = 15  # We generate 50 at a time per sub-topic
OUTPUT_DIR = "data/raw"

# The Master List of Topics you requested
# Structure: "Filename.txt": ["Subtopic 1", "Subtopic 2", ...]
TOPIC_MAP = {
    "missions.txt": [
        "The Artemis Program & Lunar Gateway (2025-2026)",
        "SpaceX Starship Development & Flight 11",
        "Voyager 1 & 2 Interstellar Status",
        "Mars Sample Return Mission Logistics",
        "History of the Apollo Program",
        "The International Space Station (End of Life Plans)",
        "Private Space Stations (Orbital Reef, Axiom)",
        "China's Tiangong Space Station",
        "Indian Space Research Organisation (Chandrayaan)",
        "The Hubble vs James Webb Telescope"
    ],
    "general.txt": [
        "NASRDA (Nigeria's Space Agency): What do they actually do?",
        "NigeriaSat-1, 2, and X: Satellites built for Nigerians",
        "The Space Barons: Elon Musk vs. Jeff Bezos (The Billionaire Race)",
        "Could a Nigerian become an astronaut? (Future Career Paths)",
        "The Gross Truth: Toilet situations and hygiene in Zero-G",
        "Space Myths: 'Juju' in space vs. Physics (Debunking superstitions)",
        "Sci-Fi vs. Reality: Black Panther/Wakanda tech vs. Real Space Tech",
        "Aliens: Are we alone or just ignoring the calls?",
        "Space Junk: Why it matters to internet in Lagos (Starlink etc)",
        "Rocket Lab & The Electron: Small rockets, big dreams"
    ],
    "blackholes.txt": [
        "Event Horizons and Spaghettification",
        "Supermassive Black Holes (Sgr A* vs M87*)",
        "Hawking Radiation & Evaporation",
        "Time Dilation near Black Holes",
        "Gravitational Waves & LIGO",
        "Primordial Black Holes",
        "Quasars and Active Galactic Nuclei",
        "The Information Paradox",
        "Wormholes (Einstein-Rosen Bridges)",
        "Neutron Stars vs Black Holes"
    ],
    "meteors.txt": [
        "The difference between Meteor, Meteoroid, Meteorite",
        "Famous Impact Craters (Chicxulub, Barringer)",
        "The Chelyabinsk Event (2013)",
        "Planetary Defense (DART Mission)",
        "Comet Tails and Outgassing",
        "The Oort Cloud vs Kuiper Belt",
        "Meteor Showers (Perseids, Geminids)",
        "Harvesting Asteroids for Mining",
        "Tunguska Event",
        "Identifying Meteorites (Fusion Crusts)"
    ],
    "astronauts.txt": [
        "Effects of Microgravity on the Human Body",
        "Psychology of Long-Duration Spaceflight",
        "Space Suits (EVA) Mechanics",
        "Famous Astronauts (Armstrong, Gagarin, Koch)",
        "Training for Space (The Neutral Buoyancy Lab)",
        "Food and Hygiene in Space",
        "Radiation Protection for Mars Crews",
        "The 'Overview Effect'",
        "Women in Space History",
        "Commercial Astronauts & Space Tourism"
    ],
    "planets.txt": [
        "The Atmosphere of Venus (Acid Rain)",
        "Geology of Mars (Olympus Mons, Valles Marineris)",
        "The Great Red Spot of Jupiter",
        "Saturn's Ring System Physics",
        "Uranus and Neptune (The Ice Giants)",
        "Mercury's Extreme Temperatures",
        "Pluto and Dwarf Planets",
        "Exoplanets (Hot Jupiters, Super-Earths)",
        "Habitable Zones (Goldilocks Zone)",
        "Formation of the Solar System"
    ],
    "spaceships.txt": [
        "Rocket Propulsion Physics (Newton's Third Law)",
        "Ion Thrusters vs Chemical Rockets",
        "Nuclear Thermal Propulsion (Future tech)",
        "The Space Shuttle (Engineering & Legacy)",
        "Soyuz Spacecraft Reliability",
        "SpaceX Falcon 9 Reusability",
        "Solar Sails",
        "Space Elevators (Theoretical)",
        "Generation Ships",
        "Warp Drives (Alcubierre Drive Theory)"
    ],
    "life_outside.txt": [
        "Europa's Subsurface Ocean",
        "Enceladus Plumes and Hydrothermal Vents",
        "Titan's Methane Lakes",
        "The Drake Equation",
        "SETI (Search for Extraterrestrial Intelligence)",
        "Biosignatures (Methane, Phosphine)",
        "Extremophiles on Earth (Analogues)",
        "The Fermi Paradox",
        "Panspermia Theory",
        "Technosignatures"
    ]
}

# --- ROBUST LOCALIZED SYSTEM PROMPT (Pan-Nigerian & Global Appeal) ---
SYSTEM_PROMPT = """
You are "UrbanSpace," a world-class Senior Science Communicator and Astrophysicist in late 2025.
Generate exactly {count} Question and Answer pairs about: {topic}.

### AUDIENCE PROFILE (Broad Appeal, Nigerian Centric)
- **Primary Audience:** Nigerians (Students, Professionals, Families) and global space enthusiasts.
- **Tone:** Intelligent, engaging, inspiring, and clear. Avoid overly casual slang that might alienate older users. Aim for a "Smart, Modern Nigerian Professional" tone (Think: A cool university lecturer).
- **Language Style:** Standard Nigerian English (British/Commonwealth spelling). Clear, articulate, and professional.
- **Localization Constraints:** - **NO Americanisms:** Use "pavement," "petrol," "football," "maths," "cinema."
  - **Units:** STRICTLY METRIC (km, m, kg, °C).
  - **Analogies:** Use relatable comparisons that almost any Nigerian would understand:
    - Distance: "Roughly the distance from Lagos to Abuja."
    - Size: "About the size of a standard football pitch."
    - Weight: "Heavier than a 50kg bag of rice."

### DEMOGRAPHIC MIX
1. **Tier 1 (The Curious Beginner):** 40% of questions. Accessible to everyone (ages 12-80). Focus on wonder, danger, and sensory details. (e.g., "Can you hear explosions in space?").
2. **Tier 2 (The Student/Career-Focused):** 40% of questions. Educational value. How things work, economic opportunities in space, and engineering.
3. **Tier 3 (The Enthusiast/Expert):** 20% of questions. Deep dives, specific dates, orbital mechanics, and technical data.

### RULES
- **Date Context:** Today is late 2025.
- **Objectivity:** When discussing private companies or nations, acknowledge global contributions (including Nigeria's NASRDA) without bias.
- **Rich Text:** Answers must be 3-6 sentences. Narrative style, not robotic.
- **Format:** Strictly Q: [Question] \\n A: [Answer] \\n\\n (Double newline separator).

Begin generation now.
"""

def generate_data():
    # Initialize the Brain
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY not found in .env")
        return

    llm = ChatGroq(
        temperature=0.7,  # Slightly creative to avoid repetition
        model_name="llama3-70b-8192", 
        api_key=api_key
    )

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Generate the data for topic: {topic}")
    ])

    chain = prompt_template | llm

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"--- STARTING SYNTHETIC DATA GENERATION ---")
    print(f"Target: ~{TARGET_PAIRS_PER_TOPIC * 10} pairs per file.")

    for filename, subtopics in TOPIC_MAP.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        print(f"\nProcessing File: {filename}")
        
        for subtopic in subtopics:
            print(f"  -> Generating: {subtopic}...", end=" ", flush=True)
            
            try:
                # Call the AI
                response = chain.invoke({
                    "topic": subtopic,
                    "count": str(TARGET_PAIRS_PER_TOPIC)
                })
                
                content = response.content
                
                # Append to file
                with open(filepath, "a", encoding="utf-8") as f:
                    f.write("\n\n" + content + "\n\n")
                
                print("Done.")
                
                # Sleep to respect Rate Limits (Groq Free Tier)
                # 30 requests per minute = 1 request every 2 seconds.
                # We sleep 25 to be safe and ensure high quality.
                time.sleep(25)
                
            except Exception as e:
                print(f"FAILED: {e}")
                time.sleep(10) # Cool down on error

    print("\n--- GENERATION COMPLETE ---")

if __name__ == "__main__":
    generate_data()