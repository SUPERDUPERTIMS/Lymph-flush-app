<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pelvic Lymphatic Drainage Protocol</title>
    <style>
        /* --- CSS STYLES --- */
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            background-color: #2a2d34;
            color: white;
        }

        .app-container {
            max-width: 400px;
            margin: 20px auto;
            padding: 20px;
            border: 1px solid #4a4e5a;
            border-radius: 10px;
            background-color: #1e2126;
            display: flex;
            flex-direction: column;
            min-height: 85vh;
        }

        .advisory-box {
            background-color: #3b2d22;
            border: 1px solid #c87d48;
            color: #f3b68c;
            padding: 10px;
            border-radius: 6px;
            font-size: 0.85em;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
        }

        .step-item {
            margin-bottom: 20px;
        }

        .title {
            color: #e99c6b;
            font-size: 1.15em;
            font-weight: bold;
            margin-bottom: 12px;
            text-transform: uppercase;
        }

        .detail-row {
            margin-bottom: 10px;
            font-size: 0.95em;
            line-height: 1.4;
        }

        .target-duration {
            font-weight: bold;
            color: #76c7c0;
            margin-top: 15px;
            font-size: 1em;
        }

        .bottom-bar {
            margin-top: auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 15px;
            border-top: 1px solid #4a4e5a;
        }

        button#start-timer-btn {
            background-color: #0066ff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 0.95em;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        button#start-timer-btn:hover {
            background-color: #0055dd;
        }

        button#manage-app-btn {
            background: none;
            border: none;
            color: #b0b5c1;
            cursor: pointer;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <!-- --- HTML STRUCTURE --- -->
    <div class="app-container">
        <!-- Technique Advisory Notice -->
        <div class="advisory-box">
            ⚠️ TECHNIQUE: Maintain steady contact and calm, controlled breathing throughout.
        </div>

        <!-- Current Step Dynamic Content Container -->
        <div id="step-content"></div>

        <!-- Bottom Action Bar -->
        <div class="bottom-bar">
            <button id="start-timer-btn">Next Step</button>
            <button id="manage-app-btn">Manage app</button>
        </div>
    </div>

    <!-- --- JAVASCRIPT LOGIC --- -->
    <script>
        /**
         * Pelvic Lymphatic Drainage Protocol - Step Sequencer Logic
         * Updated to consolidate Manual Priming and TFL Activation.
         */

        const protocolSteps = [
            {
                title: "STEP 1: OPEN PRIMARY DRAINAGE GATES",
                targetZone: "12 cm - 15 cm below navel",
                location: "Groin creases where legs meet torso, 1 cm to 2 cm inward toward pubic crease.",
                action: "Hold device stationary with a light touch for 45-60s on left side, then 45-60s on right side.",
                goal: "Unlocks primary superficial inguinal lymph nodes for fluid exit clearance.",
                duration: "90 seconds (1.5 mins)"
            },
            {
                // Here is your newly combined step based on the image
                title: "STEP 1A: CONSOLIDATED PRIMING TECHNIQUE",
                targetZone: "Superficial Inguinal Area & Tensor Fasciae Latae (TFL)",
                location: "12-15 cm below the navel (inner crease) and the outer hip muscle belly.",
                action: "PHASE 1 (30s): Device OFF. Use warm hands for a clearing effleurage (manual sweeping) toward inner nodes. <br><br>PHASE 2 (60s): Device ON (Cushion head). Apply to the TFL on the outer hip for 30s per side.",
                goal: "Safely primes primary drainage routes manually, then pre-releases lateral hip tension without stressing sensitive nodes.",
                duration: "90 seconds (1.5 mins)"
            },
            {
                title: "STEP 2: SUB-UMBILICAL MID-RELEASE",
                targetZone: "3 cm - 10 cm below navel",
                location: "Sub-umbilical zone directly below navel across a 10 cm wide band.",
                action: "Angle device at 45° downward. Using a soft attachment at low speed, perform steady, slow downward glides (~2 cm/sec) from 3 cm down to 10 cm with a featherlight touch.",
                goal: "Pre-clears mid-level fascial tightness and breaks up localized water retention.",
                duration: "45 seconds (0.75 mins)"
            },
            {
                title: "STEP 3: LOW-PELVIC GLIDE AND PAUSE CYCLE",
                targetZone: "12 cm to 15 cm below navel",
                location: "The lower pelvic boundary right where soft tissue transitions into the hard upper margin of the pubic bone.",
                action: "Using a soft attachment at medium speed (strict featherlight touch), execute a slow 30-second downward glide from 12 cm down to 15 cm. Immediately transition into a 30-second stationary pause resting against the pubic bone frame. Repeat this 60-second cycle twice.",
                goal: "Rhythmically mobilizes lower core tissue against a stable skeletal barrier, safely guiding fluid movement down to the base before the final exit sweep.",
                duration: "120 seconds (2 mins)"
            },
            {
                title: "STEP 4: OUTER HIP V-SWEEP",
                targetZone: "8 cm to 15 cm below navel",
                location: "Start from the vertical centerline (8 cm to 12 cm below navel).",
                action: "Using a soft attachment at low speed, use a featherlight touch to slowly glide downwards to 14-15 cm (just above pubic bone frame). Hold stationary for 5-10s, then curve the sweep outward and upward (2 cm to 5 cm parallel to groin line, tracking over outer hip bone/iliac crest).",
                goal: "Directs and flushes accumulated fluid safely away from sensitive areas, routing it up and over hip muscle tissue instead of into the groin crease.",
                duration: "90 seconds (1.5 mins)"
            }
        ];

        let currentStepIndex = 0;

        // Function to render the active step onto the UI
        function renderStep(index) {
            const container = document.getElementById("step-content");
            const step = protocolSteps[index];

            container.innerHTML = `
                <div class="step-item">
                    <div class="title">${step.title}</div>
                    <div class="detail-row">📍 <strong>Target Zone:</strong> ${step.targetZone}</div>
                    <div class="detail-row">🌍 <strong>Location:</strong> ${step.location}</div>
                    <div class="detail-row">⚡ <strong>Action:</strong> ${step.action}</div>
                    <div class="detail-row">🎯 <strong>Goal:</strong> ${step.goal}</div>
                    <div class="target-duration">Target Duration: ${step.duration}</div>
                </div>
            `;
        }

        // Function to handle progression through the sequence
        function handleNextStep() {
            currentStepIndex++;
            if (currentStepIndex < protocolSteps.length) {
                renderStep(currentStepIndex);
            } else {
                alert("Protocol completed successfully!");
                // Reset back to the beginning
                currentStepIndex = 0;
                renderStep(currentStepIndex);
            }
        }

        // Attach event listener to the main action button
        document.getElementById("start-timer-btn").addEventListener("click", handleNextStep);

        // Initial render call on page load
        renderStep(currentStepIndex);
    </script>
</body>
</html>
