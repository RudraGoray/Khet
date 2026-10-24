"""User-facing text in English, Hindi and Marathi.

Hindi and Marathi strings were written for this prototype and have not been reviewed by a
professional translator or by farmers. Missing keys fall back to English.
"""
from __future__ import annotations

LANGS = {"en": "English", "hi": "हिन्दी", "mr": "मराठी"}
SPEECH_LOCALE = {"en": "en-IN", "hi": "hi-IN", "mr": "mr-IN"}

T = {
    # --- shell ---
    "app_title": {"en": "KhetPlan", "hi": "खेतप्लान", "mr": "खेतप्लॅन"},
    "tagline": {
        "en": "Plan a mixed-crop season for your plot, by voice or by typing.",
        "hi": "बोलकर या लिखकर, अपने खेत के लिए मिश्रित फसल योजना बनाएं।",
        "mr": "बोलून किंवा लिहून, तुमच्या शेतासाठी मिश्र पीक नियोजन करा.",
    },
    "demo_banner": {
        "en": "Prototype. Crop numbers are synthetic demonstration values for Buldhana district only. Do not use for real planting decisions.",
        "hi": "प्रोटोटाइप। फसल के आंकड़े केवल बुलढाणा ज़िले के लिए काल्पनिक प्रदर्शन मान हैं। असली बुवाई के फ़ैसलों के लिए उपयोग न करें।",
        "mr": "प्रोटोटाइप. पिकांचे आकडे फक्त बुलढाणा जिल्ह्यासाठी काल्पनिक प्रात्यक्षिक मूल्ये आहेत. प्रत्यक्ष पेरणीच्या निर्णयासाठी वापरू नका.",
    },
    "language": {"en": "Language", "hi": "भाषा", "mr": "भाषा"},
    "step_of": {"en": "Step {i} of {n}", "hi": "चरण {i} / {n}", "mr": "टप्पा {i} / {n}"},
    "step_1": {"en": "Tell us", "hi": "बताइए", "mr": "सांगा"},
    "step_2": {"en": "Check", "hi": "जाँचें", "mr": "तपासा"},
    "step_3": {"en": "Plan", "hi": "योजना", "mr": "नियोजन"},
    "step_4": {"en": "Compare", "hi": "तुलना", "mr": "तुलना"},
    "step_5": {"en": "Print", "hi": "प्रिंट", "mr": "प्रिंट"},
    "back": {"en": "← Back", "hi": "← पीछे", "mr": "← मागे"},
    "start_over": {"en": "Start over", "hi": "फिर से शुरू करें", "mr": "पुन्हा सुरू करा"},

    # --- step 1: input ---
    "s1_title": {"en": "Tell us about your farm", "hi": "अपने खेत के बारे में बताइए", "mr": "तुमच्या शेताबद्दल सांगा"},
    "s1_prompt": {
        "en": "Say or type: where your farm is, how big it is, which season, what water you have, and how much risk you can take.",
        "hi": "बोलें या लिखें: खेत कहाँ है, कितना बड़ा है, कौन सा मौसम, पानी की क्या व्यवस्था है, और कितना जोखिम ले सकते हैं।",
        "mr": "बोला किंवा लिहा: शेत कुठे आहे, किती मोठे आहे, कोणता हंगाम, पाण्याची काय सोय आहे, आणि किती जोखीम घेऊ शकता.",
    },
    "mic_title": {"en": "Speak", "hi": "बोलें", "mr": "बोला"},
    "mic_note": {
        "en": "Voice works in Chrome or Edge. Your browser may send audio to its speech service; KhetPlan does not store audio. If the microphone does not work, type below.",
        "hi": "आवाज़ Chrome या Edge में चलती है। ब्राउज़र आवाज़ को अपनी स्पीच सेवा पर भेज सकता है; खेतप्लान आवाज़ सेव नहीं करता। माइक न चले तो नीचे लिखें।",
        "mr": "आवाज Chrome किंवा Edge मध्ये चालतो. ब्राउझर आवाज त्याच्या स्पीच सेवेकडे पाठवू शकतो; खेतप्लॅन आवाज साठवत नाही. माइक चालला नाही तर खाली लिहा.",
    },
    "transcript": {"en": "What you said (you can edit this)", "hi": "आपने जो कहा (बदल सकते हैं)", "mr": "तुम्ही जे सांगितले (बदलू शकता)"},
    "transcript_ph": {
        "en": "e.g. I have 2 acres in Buldhana, kharif season, rainfed, low risk",
        "hi": "जैसे: बुलढाणा में 2 एकड़ खेत, खरीफ, बारिश पर, कम जोखिम",
        "mr": "उदा. बुलढाणा येथे 2 एकर शेत, खरीप, कोरडवाहू, कमी जोखीम",
    },
    "examples": {"en": "Or try an example", "hi": "या एक उदाहरण आज़माएँ", "mr": "किंवा एक उदाहरण वापरा"},
    "read_details": {"en": "Read my details →", "hi": "मेरी जानकारी पढ़ें →", "mr": "माझी माहिती वाचा →"},
    "skip_manual": {"en": "Skip, fill the form myself", "hi": "छोड़ें, फ़ॉर्म खुद भरूँगा", "mr": "वगळा, फॉर्म स्वतः भरतो"},
    "mic_error": {
        "en": "Microphone or speech service problem: {detail}. Please type your details instead.",
        "hi": "माइक या स्पीच सेवा में समस्या: {detail}। कृपया जानकारी लिखें।",
        "mr": "माइक किंवा स्पीच सेवेत अडचण: {detail}. कृपया माहिती लिहा.",
    },
    "mic_stop": {"en": "Stop", "hi": "रोकें", "mr": "थांबा"},
    "mic_listening": {"en": "Listening… speak now", "hi": "सुन रहे हैं… अब बोलें", "mr": "ऐकत आहोत… आता बोला"},
    "mic_starting": {"en": "Starting microphone…", "hi": "माइक शुरू हो रहा है…", "mr": "माइक सुरू होत आहे…"},
    "mic_problem": {"en": "Microphone problem", "hi": "माइक में समस्या", "mr": "माइकमध्ये अडचण"},
    "mic_nothing": {"en": "Nothing heard. Try again or type below.", "hi": "कुछ सुनाई नहीं दिया। फिर बोलें या नीचे लिखें।", "mr": "काही ऐकू आले नाही. पुन्हा बोला किंवा खाली लिहा."},
    "mic_err_not-allowed": {"en": "microphone permission was blocked", "hi": "माइक की अनुमति रोकी गई", "mr": "माइकची परवानगी नाकारली"},
    "mic_err_service-not-allowed": {"en": "microphone permission was blocked", "hi": "माइक की अनुमति रोकी गई", "mr": "माइकची परवानगी नाकारली"},
    "mic_err_audio-capture": {"en": "no microphone was found", "hi": "माइक नहीं मिला", "mr": "माइक सापडला नाही"},
    "mic_err_no-speech": {"en": "no speech was heard", "hi": "कोई आवाज़ नहीं सुनाई दी", "mr": "आवाज ऐकू आला नाही"},
    "mic_err_network": {"en": "the browser's speech service could not be reached", "hi": "ब्राउज़र की स्पीच सेवा तक नहीं पहुँच सके", "mr": "ब्राउझरच्या स्पीच सेवेपर्यंत पोहोचता आले नाही"},
    "mic_err_unsupported-browser": {"en": "this browser has no speech recognition (try Chrome or Edge)", "hi": "इस ब्राउज़र में आवाज़ पहचान नहीं है (Chrome या Edge आज़माएँ)", "mr": "या ब्राउझरमध्ये आवाज ओळख नाही (Chrome किंवा Edge वापरा)"},
    "mic_err_no-response": {"en": "the microphone did not start", "hi": "माइक शुरू नहीं हुआ", "mr": "माइक सुरू झाला नाही"},
    "mic_err_needs-https-or-localhost": {"en": "the page must be opened over https or localhost", "hi": "पेज https या localhost पर खोलना ज़रूरी है", "mr": "पान https किंवा localhost वर उघडणे आवश्यक"},
    "mic_got": {"en": "Heard you. Check the text below.", "hi": "सुन लिया। नीचे का पाठ जाँचें।", "mr": "ऐकले. खालचा मजकूर तपासा."},

    # --- step 2: confirm ---
    "s2_title": {"en": "Check your details", "hi": "अपनी जानकारी जाँचें", "mr": "तुमची माहिती तपासा"},
    "s2_help": {
        "en": "Fields we understood are marked ✓. Fix anything wrong, fill the blanks, then confirm.",
        "hi": "जो समझ आया उस पर ✓ है। गलत ठीक करें, खाली भरें, फिर पुष्टि करें।",
        "mr": "जे समजले त्यावर ✓ आहे. चूक दुरुस्त करा, रिकामे भरा, मग खात्री करा.",
    },
    "you_said": {"en": "You said", "hi": "आपने कहा", "mr": "तुम्ही सांगितले"},
    "heard_as": {"en": "✓ understood from “{phrase}”", "hi": "✓ “{phrase}” से समझा", "mr": "✓ “{phrase}” वरून समजले"},
    "not_heard": {"en": "Please fill this in", "hi": "कृपया भरें", "mr": "कृपया भरा"},
    "f_region": {"en": "District", "hi": "ज़िला", "mr": "जिल्हा"},
    "f_area": {"en": "Plot size", "hi": "खेत का आकार", "mr": "शेताचा आकार"},
    "f_unit": {"en": "Unit", "hi": "इकाई", "mr": "एकक"},
    "f_season": {"en": "Season", "hi": "मौसम", "mr": "हंगाम"},
    "f_year": {"en": "Season year", "hi": "मौसम का वर्ष", "mr": "हंगामाचे वर्ष"},
    "f_water": {"en": "Water", "hi": "पानी", "mr": "पाणी"},
    "f_risk": {"en": "How much risk can you take?", "hi": "कितना जोखिम ले सकते हैं?", "mr": "किती जोखीम घेऊ शकता?"},
    "risk_left": {"en": "Chase higher average income", "hi": "ज़्यादा औसत कमाई", "mr": "जास्त सरासरी कमाई"},
    "risk_right": {"en": "Protect bad years", "hi": "बुरे साल से बचाव", "mr": "वाईट वर्षापासून बचाव"},
    "advanced": {"en": "More options (optional)", "hi": "और विकल्प (वैकल्पिक)", "mr": "आणखी पर्याय (ऐच्छिक)"},
    "f_exclude": {"en": "Crops you do not want", "hi": "जो फसलें नहीं चाहिए", "mr": "नको असलेली पिके"},
    "f_budget": {"en": "Cash budget for direct costs (₹, 0 = no limit)", "hi": "सीधे खर्च का बजट (₹, 0 = कोई सीमा नहीं)", "mr": "थेट खर्चाचे बजेट (₹, 0 = मर्यादा नाही)"},
    "choose": {"en": "Choose…", "hi": "चुनें…", "mr": "निवडा…"},
    "confirm_box": {"en": "These details are correct", "hi": "यह जानकारी सही है", "mr": "ही माहिती बरोबर आहे"},
    "make_plan": {"en": "Make my crop plan →", "hi": "मेरी फसल योजना बनाएं →", "mr": "माझे पीक नियोजन करा →"},
    "solving": {"en": "Finding a plan that fits your rules…", "hi": "आपके नियमों के अनुसार योजना ढूँढ रहे हैं…", "mr": "तुमच्या नियमांनुसार नियोजन शोधत आहोत…"},
    "need_confirm": {"en": "Tick the box to confirm your details.", "hi": "पुष्टि के लिए बॉक्स पर टिक करें।", "mr": "खात्रीसाठी चौकटीत टिक करा."},
    "stale": {
        "en": "Your details changed since the last plan. Confirm again to make a new plan.",
        "hi": "पिछली योजना के बाद जानकारी बदली है। नई योजना के लिए फिर से पुष्टि करें।",
        "mr": "मागील नियोजनानंतर माहिती बदलली आहे. नवीन नियोजनासाठी पुन्हा खात्री करा.",
    },

    "region_buldhana": {"en": "Buldhana, Maharashtra", "hi": "बुलढाणा, महाराष्ट्र", "mr": "बुलढाणा, महाराष्ट्र"},
    "region_other": {"en": "Other district (not supported yet)", "hi": "अन्य ज़िला (अभी समर्थित नहीं)", "mr": "इतर जिल्हा (अद्याप उपलब्ध नाही)"},
    "season_kharif": {"en": "Kharif (monsoon, Jun–Oct)", "hi": "खरीफ (बरसात, जून–अक्टूबर)", "mr": "खरीप (पावसाळा, जून–ऑक्टोबर)"},
    "season_rabi": {"en": "Rabi (winter, Oct–Mar)", "hi": "रबी (सर्दी, अक्टूबर–मार्च)", "mr": "रब्बी (हिवाळा, ऑक्टोबर–मार्च)"},
    "season_zaid": {"en": "Summer / zaid (not supported yet)", "hi": "गर्मी / जायद (अभी समर्थित नहीं)", "mr": "उन्हाळी (अद्याप उपलब्ध नाही)"},
    "unit_acre": {"en": "acre", "hi": "एकड़", "mr": "एकर"},
    "unit_hectare": {"en": "hectare", "hi": "हेक्टेयर", "mr": "हेक्टर"},
    "unit_guntha": {"en": "guntha", "hi": "गुंठा", "mr": "गुंठा"},
    "water_rainfed": {"en": "Rain only (no irrigation)", "hi": "सिर्फ़ बारिश (सिंचाई नहीं)", "mr": "फक्त पाऊस (सिंचन नाही)"},
    "water_limited": {"en": "Limited (1–2 protective irrigations, e.g. a well)", "hi": "सीमित (1–2 बचाव सिंचाई, जैसे कुआं)", "mr": "मर्यादित (1–2 संरक्षक पाणी, उदा. विहीर)"},
    "water_assured": {"en": "Assured (borewell, canal or drip)", "hi": "पक्का (बोरवेल, नहर या ड्रिप)", "mr": "खात्रीशीर (बोअरवेल, कालवा किंवा ठिबक)"},
    "risk_low": {"en": "Higher returns", "hi": "ज़्यादा कमाई", "mr": "जास्त कमाई"},
    "risk_mid": {"en": "Balanced", "hi": "संतुलित", "mr": "संतुलित"},
    "risk_high": {"en": "Safer", "hi": "ज़्यादा सुरक्षित", "mr": "जास्त सुरक्षित"},

    # --- input problems ---
    "err_missing": {"en": "{field}: required", "hi": "{field}: ज़रूरी है", "mr": "{field}: आवश्यक"},
    "err_region_unsupported": {
        "en": "{field}: this prototype only has data for Buldhana district.",
        "hi": "{field}: इस प्रोटोटाइप में केवल बुलढाणा ज़िले का डेटा है।",
        "mr": "{field}: या प्रोटोटाइपमध्ये फक्त बुलढाणा जिल्ह्याचा डेटा आहे.",
    },
    "err_season_unsupported": {
        "en": "{field}: only kharif and rabi are covered.",
        "hi": "{field}: केवल खरीफ और रबी शामिल हैं।",
        "mr": "{field}: फक्त खरीप आणि रब्बी उपलब्ध आहेत.",
    },
    "err_area_range": {
        "en": "{field}: {detail} acres is outside the supported 0.1–50 acres.",
        "hi": "{field}: {detail} एकड़ समर्थित सीमा 0.1–50 एकड़ से बाहर है।",
        "mr": "{field}: {detail} एकर हे 0.1–50 एकर मर्यादेबाहेर आहे.",
    },
    "err_area_unit": {"en": "{field}: unit not supported", "hi": "{field}: इकाई समर्थित नहीं", "mr": "{field}: एकक उपलब्ध नाही"},
    "err_budget": {"en": "{field}: must be more than zero", "hi": "{field}: शून्य से ज़्यादा होना चाहिए", "mr": "{field}: शून्यापेक्षा जास्त हवे"},
    "parse_empty": {"en": "Nothing to read yet. Speak, type, or pick an example.", "hi": "अभी कुछ नहीं है। बोलें, लिखें या उदाहरण चुनें।", "mr": "अजून काही नाही. बोला, लिहा किंवा उदाहरण निवडा."},
    "parse_area_ambiguous": {
        "en": "I heard more than one plot size ({detail}). Please enter the right one.",
        "hi": "एक से ज़्यादा आकार सुने ({detail})। सही आकार भरें।",
        "mr": "एकापेक्षा जास्त आकार ऐकले ({detail}). योग्य आकार भरा.",
    },
    "parse_unit_unsupported": {
        "en": "“{detail}” differs from place to place, so it is not supported. Please give the size in acre, guntha or hectare.",
        "hi": "“{detail}” हर जगह अलग होता है, इसलिए समर्थित नहीं। एकड़, गुंठा या हेक्टेयर में बताएं।",
        "mr": "“{detail}” ठिकाणानुसार बदलतो, म्हणून उपलब्ध नाही. एकर, गुंठा किंवा हेक्टरमध्ये सांगा.",
    },
    "parse_region_unsupported": {
        "en": "I heard “{detail}”. This prototype only has data for Buldhana district.",
        "hi": "“{detail}” सुना। इस प्रोटोटाइप में केवल बुलढाणा ज़िले का डेटा है।",
        "mr": "“{detail}” ऐकले. या प्रोटोटाइपमध्ये फक्त बुलढाणा जिल्ह्याचा डेटा आहे.",
    },
    "parse_season_unsupported": {
        "en": "I heard “{detail}”. Only kharif and rabi are covered.",
        "hi": "“{detail}” सुना। केवल खरीफ और रबी शामिल हैं।",
        "mr": "“{detail}” ऐकले. फक्त खरीप आणि रब्बी उपलब्ध आहेत.",
    },
    "parse_season_ambiguous": {
        "en": "I heard more than one season ({detail}). Please choose one.",
        "hi": "एक से ज़्यादा मौसम सुने ({detail})। एक चुनें।",
        "mr": "एकापेक्षा जास्त हंगाम ऐकले ({detail}). एक निवडा.",
    },

    # --- step 3: plan ---
    "s3_title": {"en": "Your crop plan", "hi": "आपकी फसल योजना", "mr": "तुमचे पीक नियोजन"},
    "status_OPTIMAL": {"en": "✓ Plan found and checked against every rule", "hi": "✓ योजना मिली और हर नियम पर जाँची गई", "mr": "✓ नियोजन मिळाले आणि प्रत्येक नियमावर तपासले"},
    "status_FEASIBLE": {
        "en": "✓ Valid plan found and checked (time ran out before proving it is the best)",
        "hi": "✓ मान्य योजना मिली और जाँची गई (सबसे अच्छी साबित करने से पहले समय खत्म)",
        "mr": "✓ वैध नियोजन मिळाले आणि तपासले (सर्वोत्तम सिद्ध करण्यापूर्वी वेळ संपला)",
    },
    "status_INFEASIBLE": {"en": "No plan fits all your rules", "hi": "कोई योजना सभी नियमों में फिट नहीं होती", "mr": "कोणतेही नियोजन सर्व नियमांत बसत नाही"},
    "status_TIMEOUT": {"en": "The planner ran out of time", "hi": "योजनाकार का समय खत्म हो गया", "mr": "नियोजकाचा वेळ संपला"},
    "status_INVALID_INPUT": {"en": "Some details need fixing", "hi": "कुछ जानकारी ठीक करनी है", "mr": "काही माहिती दुरुस्त करायची आहे"},
    "status_ERROR": {"en": "Something went wrong; no plan is shown", "hi": "कुछ गड़बड़ हुई; कोई योजना नहीं दिखाई गई", "mr": "काहीतरी चुकले; नियोजन दाखवले नाही"},
    "edit_details": {"en": "← Change my details", "hi": "← जानकारी बदलें", "mr": "← माहिती बदला"},
    "tab_map": {"en": "Field map", "hi": "खेत का नक्शा", "mr": "शेताचा नकाशा"},
    "tab_table": {"en": "Crops and areas", "hi": "फसलें और क्षेत्र", "mr": "पिके आणि क्षेत्र"},
    "tab_calendar": {"en": "Calendar", "hi": "कैलेंडर", "mr": "दिनदर्शिका"},
    "tab_why": {"en": "Why this plan", "hi": "यह योजना क्यों", "mr": "हे नियोजन का"},
    "map_caption": {
        "en": "The plot is drawn as {strips} equal strips ({strip_area}). Strips of each crop are spread across the plot. This is a schematic, not a measured layout.",
        "hi": "खेत को {strips} बराबर पट्टियों ({strip_area}) में दिखाया गया है। हर फसल की पट्टियाँ पूरे खेत में फैली हैं। यह एक रेखाचित्र है, नापा हुआ नक्शा नहीं।",
        "mr": "शेत {strips} समान पट्ट्यांमध्ये ({strip_area}) दाखवले आहे. प्रत्येक पिकाच्या पट्ट्या शेतभर पसरल्या आहेत. हे रेखाचित्र आहे, मोजलेला नकाशा नाही.",
    },
    "col_crop": {"en": "Crop", "hi": "फसल", "mr": "पीक"},
    "col_share": {"en": "Share", "hi": "हिस्सा", "mr": "वाटा"},
    "col_area": {"en": "Area", "hi": "क्षेत्र", "mr": "क्षेत्र"},
    "col_strips": {"en": "Strips", "hi": "पट्टियाँ", "mr": "पट्ट्या"},
    "col_sow": {"en": "Sow", "hi": "बुवाई", "mr": "पेरणी"},
    "col_harvest": {"en": "Harvest", "hi": "कटाई", "mr": "काढणी"},
    "col_irrigation": {"en": "Irrigation need", "hi": "सिंचाई ज़रूरत", "mr": "सिंचन गरज"},
    "col_cost": {"en": "Direct cost", "hi": "सीधा खर्च", "mr": "थेट खर्च"},
    "col_gross_normal": {"en": "Gross revenue, normal year", "hi": "सकल आय, सामान्य साल", "mr": "एकूण उत्पन्न, सामान्य वर्ष"},
    "kpi_area": {"en": "Plot", "hi": "खेत", "mr": "शेत"},
    "kpi_crops": {"en": "Crops", "hi": "फसलें", "mr": "पिके"},
    "kpi_water": {"en": "Irrigation used / available", "hi": "सिंचाई उपयोग / उपलब्ध", "mr": "सिंचन वापर / उपलब्ध"},
    "kpi_cost": {"en": "Direct cash cost", "hi": "सीधा नकद खर्च", "mr": "थेट रोख खर्च"},
    "growing": {"en": "Growing", "hi": "बढ़त", "mr": "वाढ"},
    "harvesting": {"en": "Harvest and sale", "hi": "कटाई और बिक्री", "mr": "काढणी आणि विक्री"},
    "to_compare": {"en": "Compare with a single crop →", "hi": "एक फसल से तुलना करें →", "mr": "एका पिकाशी तुलना करा →"},
    "checks_title": {"en": "Rule checks (run independently of the planner)", "hi": "नियम जाँच (योजनाकार से अलग चलाई गई)", "mr": "नियम तपासणी (नियोजकापासून स्वतंत्र)"},
    "check_area": {"en": "All {acres} of the plot is used, no more, no less", "hi": "पूरा {acres} खेत उपयोग में, न ज़्यादा न कम", "mr": "संपूर्ण {acres} शेत वापरले, कमी नाही जास्त नाही"},
    "check_water": {"en": "Irrigation need fits the water you have", "hi": "सिंचाई की ज़रूरत उपलब्ध पानी में", "mr": "सिंचनाची गरज उपलब्ध पाण्यात"},
    "check_pairs": {"en": "Every crop pair is a supported combination", "hi": "हर फसल जोड़ी समर्थित है", "mr": "प्रत्येक पीक जोडी उपलब्ध आहे"},
    "check_season": {"en": "Every crop belongs to this district and season", "hi": "हर फसल इस ज़िले और मौसम की है", "mr": "प्रत्येक पीक या जिल्हा व हंगामातील आहे"},
    "check_shares": {"en": "Each crop's share is within its allowed range", "hi": "हर फसल का हिस्सा अनुमत सीमा में", "mr": "प्रत्येक पिकाचा वाटा परवानगी मर्यादेत"},
    "check_budget": {"en": "Direct cost fits your budget", "hi": "सीधा खर्च बजट में", "mr": "थेट खर्च बजेटमध्ये"},
    "check_excluded": {"en": "No crop you rejected is used", "hi": "आपकी मना की गई कोई फसल नहीं", "mr": "तुम्ही नाकारलेले पीक वापरले नाही"},

    # --- explanations ---
    "exp_objective": {
        "en": "Your risk setting is {risk}/100. The planner scores each option as {pct_mean}% average net margin plus {pct_cvar}% of the average in the worst 10% of simulated seasons, with a small bonus for harvests spread over more months. The risk setting changes only this scoring, never the rules below.",
        "hi": "आपकी जोखिम सेटिंग {risk}/100 है। योजनाकार हर विकल्प को {pct_mean}% औसत शुद्ध मार्जिन और {pct_cvar}% सबसे खराब 10% मौसमों के औसत से आंकता है, और ज़्यादा महीनों में फैली कटाई पर थोड़ा बोनस देता है। जोखिम सेटिंग सिर्फ़ यह अंक बदलती है, नीचे के नियम कभी नहीं।",
        "mr": "तुमची जोखीम पातळी {risk}/100 आहे. नियोजक प्रत्येक पर्यायाला {pct_mean}% सरासरी निव्वळ नफा आणि {pct_cvar}% सर्वात वाईट 10% हंगामांची सरासरी यावर गुण देतो, आणि जास्त महिन्यांत पसरलेल्या काढणीला थोडा बोनस देतो. जोखीम पातळी फक्त हे गुण बदलते, खालील नियम कधीच नाही.",
    },
    "exp_area": {
        "en": "Rule: the whole plot ({acres}) is split into {strips} strips of {strip_acres} each, so shares move in 5% steps.",
        "hi": "नियम: पूरा खेत ({acres}) {strips} पट्टियों में बँटा है, हर पट्टी {strip_acres}, इसलिए हिस्सा 5% के कदमों में बदलता है।",
        "mr": "नियम: संपूर्ण शेत ({acres}) {strips} पट्ट्यांमध्ये विभागले आहे, प्रत्येक {strip_acres}, म्हणून वाटा 5% च्या टप्प्यांत बदलतो.",
    },
    "exp_water": {
        "en": "Rule: average irrigation need must not exceed {limit} mm for “{level}”. This plan needs {used} mm.{binding}",
        "hi": "नियम: “{level}” के लिए औसत सिंचाई ज़रूरत {limit} मिमी से ज़्यादा नहीं हो सकती। इस योजना को {used} मिमी चाहिए।{binding}",
        "mr": "नियम: “{level}” साठी सरासरी सिंचन गरज {limit} मिमीपेक्षा जास्त नसावी. या नियोजनाला {used} मिमी लागते.{binding}",
    },
    "exp_water_binding": {"en": " Water is the limiting rule here.", "hi": " यहाँ पानी ही सीमित करने वाला नियम है।", "mr": " येथे पाणी हाच मर्यादित करणारा नियम आहे."},
    "exp_water_limits": {
        "en": "These crops need more irrigation than your limit, so they can take only part of the plot, or none if you rely on rain: {crops}.",
        "hi": "इन फसलों को आपकी सीमा से ज़्यादा सिंचाई चाहिए, इसलिए ये खेत का सिर्फ़ कुछ हिस्सा ले सकती हैं, या बारिश पर निर्भर होने पर बिल्कुल नहीं: {crops}।",
        "mr": "या पिकांना तुमच्या मर्यादेपेक्षा जास्त सिंचन लागते, म्हणून ती शेताचा काही भागच घेऊ शकतात, किंवा पावसावर अवलंबून असल्यास अजिबात नाही: {crops}.",
    },
    "exp_budget": {
        "en": "Rule: direct cost ₹{cost} must stay within your budget of ₹{budget}.",
        "hi": "नियम: सीधा खर्च ₹{cost} आपके बजट ₹{budget} के अंदर रहना चाहिए।",
        "mr": "नियम: थेट खर्च ₹{cost} तुमच्या ₹{budget} बजेटमध्ये असावा.",
    },
    "exp_pairs": {
        "en": "Rule: every pair of crops must be a combination listed in the dataset. {crops} meet this.",
        "hi": "नियम: हर फसल जोड़ी डेटासेट में दी गई होनी चाहिए। {crops} इस पर खरे हैं।",
        "mr": "नियम: प्रत्येक पीक जोडी डेटासेटमध्ये असावी. {crops} हे पूर्ण करतात.",
    },
    "exp_shares": {
        "en": "Rule: each chosen crop gets {min}–{max} of the plot, and a plan uses 2 to {max_crops} crops.",
        "hi": "नियम: हर चुनी फसल को खेत का {min}–{max} मिलता है, और योजना में 2 से {max_crops} फसलें होती हैं।",
        "mr": "नियम: प्रत्येक निवडलेल्या पिकाला शेताचा {min}–{max} मिळतो, आणि नियोजनात 2 ते {max_crops} पिके असतात.",
    },
    "exp_crop": {
        "en": "{crops}: {share} of the plot. Simulated average net margin ₹{mean}/acre (spread ±₹{sd}).{limit}",
        "hi": "{crops}: खेत का {share}। अनुमानित औसत शुद्ध मार्जिन ₹{mean}/एकड़ (उतार-चढ़ाव ±₹{sd})।{limit}",
        "mr": "{crops}: शेताचा {share}. अंदाजित सरासरी निव्वळ नफा ₹{mean}/एकर (चढउतार ±₹{sd}).{limit}",
    },
    "exp_limit_max": {"en": " Held at its maximum share.", "hi": " अधिकतम हिस्से पर।", "mr": " कमाल वाट्यावर."},
    "exp_limit_min": {"en": " Kept at its minimum share.", "hi": " न्यूनतम हिस्से पर।", "mr": " किमान वाट्यावर."},
    "exp_farmer_excluded": {"en": "You asked to leave out {crops}.", "hi": "आपने {crops} हटाने को कहा।", "mr": "तुम्ही {crops} वगळायला सांगितले."},
    "exp_dataset_excluded": {
        "en": "Not considered because the dataset does not cover them yet: {crops}.",
        "hi": "विचार नहीं किया क्योंकि डेटासेट में अभी इनकी जानकारी नहीं: {crops}।",
        "mr": "विचार केला नाही कारण डेटासेटमध्ये अजून यांची माहिती नाही: {crops}.",
    },
    "diag_infeasible": {
        "en": "No mix of 2–3 crops satisfies all the rules together. Nothing was relaxed automatically.",
        "hi": "2–3 फसलों का कोई मेल सभी नियम एक साथ पूरे नहीं करता। कुछ भी अपने आप ढीला नहीं किया गया।",
        "mr": "2–3 पिकांचा कोणताही मेळ सर्व नियम एकत्र पूर्ण करत नाही. काहीही आपोआप शिथिल केले नाही.",
    },
    "diag_lift_water": {"en": "More water would make a plan possible.", "hi": "ज़्यादा पानी से योजना संभव होगी।", "mr": "जास्त पाण्याने नियोजन शक्य होईल."},
    "diag_lift_budget": {"en": "A larger cash budget would make a plan possible.", "hi": "बड़े बजट से योजना संभव होगी।", "mr": "मोठ्या बजेटने नियोजन शक्य होईल."},
    "diag_lift_shares": {"en": "The minimum/maximum crop shares are what block a plan.", "hi": "फसल हिस्सों की न्यूनतम/अधिकतम सीमा योजना रोक रही है।", "mr": "पीक वाट्याच्या किमान/कमाल मर्यादा नियोजन अडवत आहेत."},
    "diag_lift_pairs": {
        "en": "The remaining crops have no supported pairing. Allow more crops (fewer exclusions).",
        "hi": "बची फसलों की कोई समर्थित जोड़ी नहीं है। कम फसलें हटाएँ।",
        "mr": "उरलेल्या पिकांची कोणतीही उपलब्ध जोडी नाही. कमी पिके वगळा.",
    },
    "diag_multiple": {"en": "More than one rule would need to change.", "hi": "एक से ज़्यादा नियम बदलने होंगे।", "mr": "एकापेक्षा जास्त नियम बदलावे लागतील."},
    "diag_too_few_crops": {
        "en": "Only {count} crop(s) remain after exclusions; an intercrop plan needs at least 2.",
        "hi": "हटाने के बाद केवल {count} फसल बची; मिश्रित योजना के लिए कम से कम 2 चाहिए।",
        "mr": "वगळल्यानंतर फक्त {count} पीक उरले; मिश्र नियोजनासाठी किमान 2 हवीत.",
    },
    "diag_timeout": {"en": "Try again; if it repeats, simplify the options.", "hi": "फिर से कोशिश करें।", "mr": "पुन्हा प्रयत्न करा."},
    "diag_error": {"en": "Solver error: {detail}", "hi": "सॉल्वर त्रुटि: {detail}", "mr": "सॉल्व्हर त्रुटी: {detail}"},
    "diag_validation": {
        "en": "The planner's answer failed the independent rule check, so it is not shown: {detail}",
        "hi": "योजनाकार का उत्तर स्वतंत्र जाँच में विफल रहा, इसलिए नहीं दिखाया: {detail}",
        "mr": "नियोजकाचे उत्तर स्वतंत्र तपासणीत अयशस्वी, म्हणून दाखवले नाही: {detail}",
    },

    # --- step 4: compare ---
    "s4_title": {"en": "How does the plan hold up?", "hi": "योजना कितनी टिकाऊ है?", "mr": "नियोजन किती टिकाऊ आहे?"},
    "s4_help": {
        "en": "We replay {n} simulated seasons (good and bad weather, price swings, crop losses) on your mixed plan and on a single-crop plan. Both plans face exactly the same seasons.",
        "hi": "हम {n} काल्पनिक मौसम (अच्छा-बुरा मौसम, भाव में उतार-चढ़ाव, फसल नुकसान) आपकी मिश्रित योजना और एक-फसल योजना पर चलाते हैं। दोनों पर बिल्कुल वही मौसम।",
        "mr": "आम्ही {n} काल्पनिक हंगाम (चांगले-वाईट हवामान, भावातील चढउतार, पीक नुकसान) तुमच्या मिश्र नियोजनावर आणि एक-पीक नियोजनावर चालवतो. दोघांवर अगदी तेच हंगाम.",
    },
    "baseline": {"en": "Single crop to compare with", "hi": "तुलना के लिए एक फसल", "mr": "तुलनेसाठी एक पीक"},
    "baseline_help": {
        "en": "Only single crops that fit your district, season, water and budget are listed. The default is the one with the highest simulated average net margin.",
        "hi": "सिर्फ़ वही फसलें जो आपके ज़िले, मौसम, पानी और बजट में फिट हैं। डिफ़ॉल्ट वह है जिसका औसत शुद्ध मार्जिन सबसे ज़्यादा है।",
        "mr": "फक्त तुमच्या जिल्हा, हंगाम, पाणी आणि बजेटमध्ये बसणारी पिके. डिफॉल्ट म्हणजे सर्वाधिक सरासरी निव्वळ नफा असलेले.",
    },
    "no_baseline": {
        "en": "No single crop can legally fill the whole plot under your water and budget rules, so no fair comparison is possible.",
        "hi": "आपके पानी और बजट नियमों में कोई एक फसल पूरा खेत नहीं ले सकती, इसलिए उचित तुलना संभव नहीं।",
        "mr": "तुमच्या पाणी आणि बजेट नियमांत कोणतेही एक पीक संपूर्ण शेत घेऊ शकत नाही, म्हणून योग्य तुलना शक्य नाही.",
    },
    "seed_short": {"en": "Seed", "hi": "सीड", "mr": "सीड"},
    "seed": {"en": "Random seed (same seed = same results)", "hi": "रैंडम सीड (एक सीड = एक परिणाम)", "mr": "रँडम सीड (समान सीड = समान निकाल)"},
    "run_sim": {"en": "Run 1,000 seasons", "hi": "1,000 मौसम चलाएँ", "mr": "1,000 हंगाम चालवा"},
    "simulating": {"en": "Simulating seasons…", "hi": "मौसम चल रहे हैं…", "mr": "हंगाम चालू आहेत…"},
    "mixed_plan": {"en": "Mixed plan", "hi": "मिश्रित योजना", "mr": "मिश्र नियोजन"},
    "single_plan": {"en": "Only {crop}", "hi": "सिर्फ़ {crop}", "mr": "फक्त {crop}"},
    "m_mean_gross": {"en": "Average gross revenue (before costs)", "hi": "औसत सकल आय (खर्च से पहले)", "mr": "सरासरी एकूण उत्पन्न (खर्चापूर्वी)"},
    "m_cost": {"en": "Direct cash cost (assumed fixed)", "hi": "सीधा नकद खर्च (स्थिर माना)", "mr": "थेट रोख खर्च (स्थिर मानला)"},
    "m_mean_net": {"en": "Average net margin (gross − direct cost)", "hi": "औसत शुद्ध मार्जिन (सकल − सीधा खर्च)", "mr": "सरासरी निव्वळ नफा (एकूण − थेट खर्च)"},
    "m_p10_net": {"en": "Bad-year net margin (10th percentile)", "hi": "खराब साल का शुद्ध मार्जिन (10वाँ प्रतिशतक)", "mr": "वाईट वर्षाचा निव्वळ नफा (10 वा शतमक)"},
    "m_p10_gross": {"en": "Bad-year gross revenue (10th percentile)", "hi": "खराब साल की सकल आय (10वाँ प्रतिशतक)", "mr": "वाईट वर्षाचे एकूण उत्पन्न (10 वा शतमक)"},
    "m_sd_net": {"en": "Year-to-year swing in net margin (std. dev.)", "hi": "साल-दर-साल शुद्ध मार्जिन में उतार-चढ़ाव (मानक विचलन)", "mr": "वर्षानुवर्षे निव्वळ नफ्यातील चढउतार (मानक विचलन)"},
    "m_cv_net": {"en": "Variability (CV of net margin)", "hi": "अस्थिरता (शुद्ध मार्जिन का CV)", "mr": "अस्थिरता (निव्वळ नफ्याचा CV)"},
    "m_prob_loss": {"en": "Chance of losing money (net < 0)", "hi": "घाटे की संभावना (शुद्ध < 0)", "mr": "तोट्याची शक्यता (निव्वळ < 0)"},
    "m_zero_months": {"en": "Months with zero farm income (of 12, average)", "hi": "बिना खेती आय के महीने (12 में से, औसत)", "mr": "शेती उत्पन्न नसलेले महिने (12 पैकी, सरासरी)"},
    "m_metric": {"en": "Measure", "hi": "माप", "mr": "माप"},
    "m_diff": {"en": "Difference", "hi": "अंतर", "mr": "फरक"},
    "undefined": {"en": "n/a (average near zero)", "hi": "लागू नहीं (औसत लगभग शून्य)", "mr": "लागू नाही (सरासरी जवळपास शून्य)"},
    "verdict": {
        "en": "In {share} of the same simulated seasons, the mixed plan earned a higher net margin than only {crop}. On average it earned ₹{diff} {more_less}. In a bad year (10th percentile) it earned {p10} versus {p10b}.",
        "hi": "उन्हीं काल्पनिक मौसमों में से {share} में मिश्रित योजना का शुद्ध मार्जिन सिर्फ़ {crop} से ज़्यादा रहा। औसतन यह ₹{diff} {more_less} रहा। खराब साल (10वाँ प्रतिशतक) में {p10} बनाम {p10b}।",
        "mr": "त्याच काल्पनिक हंगामांपैकी {share} मध्ये मिश्र नियोजनाचा निव्वळ नफा फक्त {crop} पेक्षा जास्त होता. सरासरी तो ₹{diff} {more_less} होता. वाईट वर्षात (10 वा शतमक) {p10} विरुद्ध {p10b}.",
    },
    "more": {"en": "more", "hi": "ज़्यादा", "mr": "जास्त"},
    "less": {"en": "less", "hi": "कम", "mr": "कमी"},
    "verdict_honest": {
        "en": "Diversifying is not guaranteed to pay. These numbers come straight from the simulation, whichever plan comes out ahead.",
        "hi": "मिश्रित खेती हमेशा फ़ायदेमंद हो, ज़रूरी नहीं। ये आंकड़े सीधे सिमुलेशन से हैं, चाहे कोई भी योजना आगे हो।",
        "mr": "मिश्र शेती नेहमी फायद्याची असेलच असे नाही. हे आकडे थेट सिम्युलेशनमधून आहेत, कोणतेही नियोजन पुढे असो.",
    },
    "chart_dist": {"en": "Net margin across simulated seasons", "hi": "काल्पनिक मौसमों में शुद्ध मार्जिन", "mr": "काल्पनिक हंगामांतील निव्वळ नफा"},
    "chart_monthly": {"en": "Average gross revenue by month (sales during harvest)", "hi": "महीनेवार औसत सकल आय (कटाई पर बिक्री)", "mr": "महिनावार सरासरी एकूण उत्पन्न (काढणीवेळी विक्री)"},
    "chart_diff": {"en": "Mixed minus single crop, same season (net margin)", "hi": "मिश्रित माइनस एक फसल, वही मौसम (शुद्ध मार्जिन)", "mr": "मिश्र वजा एक पीक, तोच हंगाम (निव्वळ नफा)"},
    "axis_net": {"en": "Net margin per season (₹)", "hi": "प्रति मौसम शुद्ध मार्जिन (₹)", "mr": "प्रति हंगाम निव्वळ नफा (₹)"},
    "axis_seasons": {"en": "Number of seasons", "hi": "मौसमों की संख्या", "mr": "हंगामांची संख्या"},
    "axis_gross_month": {"en": "Gross revenue (₹)", "hi": "सकल आय (₹)", "mr": "एकूण उत्पन्न (₹)"},
    "axis_diff": {"en": "Mixed − single (₹)", "hi": "मिश्रित − एक फसल (₹)", "mr": "मिश्र − एक पीक (₹)"},
    "p10_line": {"en": "10th percentile", "hi": "10वाँ प्रतिशतक", "mr": "10 वा शतमक"},
    "sim_disclaimer": {
        "en": "Illustrative simulation, not a forecast or guarantee. Weather odds, price swings, yields, costs and loss rates are synthetic assumptions. Costs are assumed fixed; family labour, land rent and interest are not counted.",
        "hi": "उदाहरण के लिए सिमुलेशन, पूर्वानुमान या गारंटी नहीं। मौसम की संभावना, भाव, उपज, खर्च और नुकसान दर काल्पनिक मान्यताएँ हैं। खर्च स्थिर माना है; परिवार की मज़दूरी, ज़मीन किराया और ब्याज शामिल नहीं।",
        "mr": "उदाहरणादाखल सिम्युलेशन, अंदाज किंवा हमी नाही. हवामान शक्यता, भाव, उत्पादन, खर्च आणि नुकसान दर काल्पनिक गृहितके आहेत. खर्च स्थिर मानला; कुटुंबाची मजुरी, जमीन भाडे आणि व्याज धरलेले नाही.",
    },
    "to_print": {"en": "Make printable summary →", "hi": "प्रिंट करने लायक सारांश बनाएं →", "mr": "छापण्यायोग्य सारांश बनवा →"},
    "skip_compare": {"en": "Skip comparison, go to summary", "hi": "तुलना छोड़ें, सारांश पर जाएँ", "mr": "तुलना वगळा, सारांशाकडे जा"},

    # --- step 5: print ---
    "s5_title": {"en": "Printable summary", "hi": "प्रिंट सारांश", "mr": "छापण्यायोग्य सारांश"},
    "s5_help": {
        "en": "One A4 page built from your confirmed details, the checked plan and the simulation above. Download it, open it in a browser, and print or save as PDF.",
        "hi": "आपकी पुष्टि की गई जानकारी, जाँची गई योजना और ऊपर के सिमुलेशन से बना एक A4 पेज। डाउनलोड करें, ब्राउज़र में खोलें और प्रिंट या PDF करें।",
        "mr": "तुमची खात्री केलेली माहिती, तपासलेले नियोजन आणि वरील सिम्युलेशनमधून बनलेले एक A4 पान. डाउनलोड करा, ब्राउझरमध्ये उघडा आणि प्रिंट किंवा PDF करा.",
    },
    "download_html": {"en": "Download summary (HTML, print-ready)", "hi": "सारांश डाउनलोड करें (HTML, प्रिंट के लिए)", "mr": "सारांश डाउनलोड करा (HTML, छपाईसाठी)"},
    "download_json": {"en": "Download plan data (JSON)", "hi": "योजना डेटा डाउनलोड करें (JSON)", "mr": "नियोजन डेटा डाउनलोड करा (JSON)"},
    "print_now": {"en": "🖨 Print", "hi": "🖨 प्रिंट", "mr": "🖨 प्रिंट"},
    "no_sim_note": {"en": "Comparison not run, so the summary has no simulation results.", "hi": "तुलना नहीं चलाई, इसलिए सारांश में सिमुलेशन नतीजे नहीं हैं।", "mr": "तुलना चालवली नाही, म्हणून सारांशात सिम्युलेशन निकाल नाहीत."},

    # --- summary document ---
    "sum_title": {"en": "KhetPlan crop plan summary", "hi": "खेतप्लान फसल योजना सारांश", "mr": "खेतप्लॅन पीक नियोजन सारांश"},
    "sum_farm": {"en": "Farm details (confirmed by farmer)", "hi": "खेत की जानकारी (किसान द्वारा पुष्ट)", "mr": "शेताची माहिती (शेतकऱ्याने खात्री केलेली)"},
    "sum_plan": {"en": "Crop plan", "hi": "फसल योजना", "mr": "पीक नियोजन"},
    "sum_rules": {"en": "Rules applied", "hi": "लागू नियम", "mr": "लागू नियम"},
    "sum_sim": {"en": "Simulated comparison", "hi": "सिमुलेटेड तुलना", "mr": "सिम्युलेटेड तुलना"},
    "sum_about": {"en": "About these numbers", "hi": "इन आंकड़ों के बारे में", "mr": "या आकड्यांबद्दल"},
    "sum_generated": {"en": "Generated", "hi": "बनाया गया", "mr": "तयार केले"},
    "sum_dataset": {"en": "Dataset", "hi": "डेटासेट", "mr": "डेटासेट"},
    "sum_data_note": {
        "en": "All crop values (yields, prices, costs, water needs, dates) are synthetic demonstration assumptions for Buldhana district, not observed data, and have not been reviewed by an agronomist. Check with your local Krishi Vigyan Kendra or agriculture officer before planting.",
        "hi": "सभी फसल मान (उपज, भाव, खर्च, पानी, तारीखें) बुलढाणा ज़िले के लिए काल्पनिक प्रदर्शन मान्यताएँ हैं, असली आंकड़े नहीं, और किसी कृषि विशेषज्ञ ने इनकी समीक्षा नहीं की। बुवाई से पहले अपने कृषि विज्ञान केंद्र या कृषि अधिकारी से सलाह लें।",
        "mr": "सर्व पीक मूल्ये (उत्पादन, भाव, खर्च, पाणी, तारखा) बुलढाणा जिल्ह्यासाठी काल्पनिक प्रात्यक्षिक गृहितके आहेत, प्रत्यक्ष आकडे नाहीत, आणि कृषी तज्ज्ञाने तपासलेली नाहीत. पेरणीपूर्वी तुमच्या कृषी विज्ञान केंद्र किंवा कृषी अधिकाऱ्याचा सल्ला घ्या.",
    },
    # --- digital twin and dashboard ---
    "sales": {"en": "Sales so far", "hi": "अब तक बिक्री", "mr": "आतापर्यंत विक्री"},
    "water_week": {"en": "Water this week", "hi": "इस हफ़्ते पानी", "mr": "या आठवड्यात पाणी"},
    "labour_week": {"en": "Labour this week", "hi": "इस हफ़्ते मज़दूरी", "mr": "या आठवड्यात मजुरी"},
    "plot": {"en": "Plot", "hi": "खेत", "mr": "शेत"},
    "water": {"en": "Water", "hi": "पानी", "mr": "पाणी"},
    "season": {"en": "Season", "hi": "मौसम", "mr": "हंगाम"},
    "person_days": {"en": "person-days", "hi": "व्यक्ति-दिन", "mr": "मनुष्य-दिवस"},
    "acre": {"en": "acre", "hi": "एकड़", "mr": "एकर"},
    "week_of": {"en": "Week {i} of {n}", "hi": "हफ़्ता {i} / {n}", "mr": "आठवडा {i} / {n}"},
    "mini_title": {"en": "Weekly water · cumulative sales", "hi": "हफ़्तेवार पानी · कुल बिक्री", "mr": "आठवडावार पाणी · एकूण विक्री"},
    "legend_water": {"en": "Water use", "hi": "पानी उपयोग", "mr": "पाणी वापर"},
    "legend_sales": {"en": "Sales", "hi": "बिक्री", "mr": "विक्री"},
    "legend_ref": {"en": "Planned", "hi": "योजना", "mr": "नियोजन"},
    "health": {"en": "Crop health", "hi": "फसल स्वास्थ्य", "mr": "पीक आरोग्य"},
    "harvested": {"en": "Harvested", "hi": "कटा", "mr": "काढले"},
    "sow_on": {"en": "Sowing", "hi": "बुवाई", "mr": "पेरणी"},
    "strip": {"en": "Strip", "hi": "पट्टी", "mr": "पट्टा"},
    "all_crops": {"en": "all crops", "hi": "सभी फसलें", "mr": "सर्व पिके"},
    "intro_plan": {"en": "Planting your field…", "hi": "आपका खेत बोया जा रहा है…", "mr": "तुमचे शेत पेरले जात आहे…"},
    "intro_plan_sub": {"en": "Press ▶ or drag the timeline to live through the season", "hi": "▶ दबाएँ या टाइमलाइन खींचें", "mr": "▶ दाबा किंवा टाइमलाइन ओढा"},
    "intro_preview": {"en": "Your field, built from your details", "hi": "आपकी जानकारी से बना आपका खेत", "mr": "तुमच्या माहितीवरून बनलेले शेत"},
    "intro_preview_sub": {"en": "Confirm the details to plant it", "hi": "बोने के लिए जानकारी की पुष्टि करें", "mr": "पेरण्यासाठी माहितीची खात्री करा"},
    "wx_rain": {"en": "Monsoon rain", "hi": "मानसूनी बारिश", "mr": "मान्सून पाऊस"},
    "wx_dry": {"en": "Dry spell", "hi": "सूखे का दौर", "mr": "कोरडा काळ"},
    "wx_clear": {"en": "Clear sky", "hi": "साफ़ आसमान", "mr": "निरभ्र आकाश"},
    "ev_sow": {"en": "Sowing · {crop}", "hi": "बुवाई · {crop}", "mr": "पेरणी · {crop}"},
    "ev_flower": {"en": "Flowering · {crop}", "hi": "फूल · {crop}", "mr": "फुलोरा · {crop}"},
    "ev_harvest": {"en": "Harvest starts · {crop}", "hi": "कटाई शुरू · {crop}", "mr": "काढणी सुरू · {crop}"},
    "ev_done": {"en": "Harvest done · {crop}", "hi": "कटाई पूरी · {crop}", "mr": "काढणी पूर्ण · {crop}"},
    "ev_dry_spell": {"en": "Dry spell begins", "hi": "सूखा दौर शुरू", "mr": "कोरडा काळ सुरू"},
    "ev_pest": {"en": "Pest attack · {crop}", "hi": "कीट हमला · {crop}", "mr": "कीड हल्ला · {crop}"},
    "ev_price": {"en": "Price change · {crop}", "hi": "भाव बदला · {crop}", "mr": "भाव बदल · {crop}"},
    "ev_water_cut": {"en": "Water supply cut", "hi": "पानी की कटौती", "mr": "पाणी कपात"},
    "stage_0": {"en": "Not sown", "hi": "बोया नहीं", "mr": "पेरले नाही"},
    "stage_1": {"en": "Germinating", "hi": "अंकुरण", "mr": "उगवण"},
    "stage_2": {"en": "Growing", "hi": "बढ़वार", "mr": "वाढ"},
    "stage_3": {"en": "Flowering", "hi": "फूल", "mr": "फुलोरा"},
    "stage_4": {"en": "Ripening", "hi": "पकना", "mr": "पक्वता"},
    "stage_5": {"en": "Harvesting", "hi": "कटाई", "mr": "काढणी"},
    "stage_6": {"en": "Harvested", "hi": "कटाई पूरी", "mr": "काढणी पूर्ण"},
    "water_short_rainfed": {"en": "Rain only", "hi": "सिर्फ़ बारिश", "mr": "फक्त पाऊस"},
    "water_short_limited": {"en": "Well (limited)", "hi": "कुआं (सीमित)", "mr": "विहीर (मर्यादित)"},
    "water_short_assured": {"en": "Borewell / drip", "hi": "बोरवेल / ड्रिप", "mr": "बोअरवेल / ठिबक"},
    "season_short_kharif": {"en": "Kharif", "hi": "खरीफ", "mr": "खरीप"},
    "season_short_rabi": {"en": "Rabi", "hi": "रबी", "mr": "रब्बी"},
    "twin_preview_title": {"en": "Your plot", "hi": "आपका खेत", "mr": "तुमचे शेत"},
    "twin_empty_title": {"en": "Your farm appears here", "hi": "आपका खेत यहाँ दिखेगा", "mr": "तुमचे शेत येथे दिसेल"},
    "twin_preview_sub": {"en": "3D preview · confirm to plant", "hi": "3D झलक · बोने के लिए पुष्टि करें", "mr": "3D झलक · पेरण्यासाठी खात्री करा"},
    "hero_kicker": {"en": "FARM DIGITAL TWIN", "hi": "खेत का डिजिटल ट्विन", "mr": "शेताचा डिजिटल ट्विन"},
    "hero_title": {"en": "Speak your farm. See your season.", "hi": "अपना खेत बोलिए। अपना मौसम देखिए।", "mr": "तुमचे शेत सांगा. तुमचा हंगाम पाहा."},
    "hero_sub": {"en": "Describe your plot by voice. KhetPlan builds a 3D twin of your field, plants a checked mixed-crop plan on it, and lets you live through the season week by week.", "hi": "आवाज़ से अपना खेत बताइए। खेतप्लान आपके खेत का 3D ट्विन बनाता है, उस पर जाँची हुई मिश्रित फसल योजना लगाता है, और आपको हफ़्ता-दर-हफ़्ता पूरा मौसम दिखाता है।", "mr": "आवाजाने तुमचे शेत सांगा. खेतप्लॅन तुमच्या शेताचा 3D ट्विन बनवतो, त्यावर तपासलेले मिश्र पीक नियोजन लावतो, आणि आठवड्यागणिक संपूर्ण हंगाम दाखवतो."},
    "panel_voice": {"en": "1 · Talk to KhetPlan", "hi": "1 · खेतप्लान से बात करें", "mr": "1 · खेतप्लॅनशी बोला"},
    "panel_details": {"en": "2 · Check what we understood", "hi": "2 · जो समझा उसे जाँचें", "mr": "2 · जे समजले ते तपासा"},
    "build_farm": {"en": "🌱 Build my farm plan", "hi": "🌱 मेरी खेत योजना बनाएं", "mr": "🌱 माझे शेत नियोजन करा"},
    "edit_farm": {"en": "Edit farm details", "hi": "खेत की जानकारी बदलें", "mr": "शेताची माहिती बदला"},
    "plan_card": {"en": "Your plan", "hi": "आपकी योजना", "mr": "तुमचे नियोजन"},
    "tab_twin_plan": {"en": "📋 Plan & rules", "hi": "📋 योजना और नियम", "mr": "📋 नियोजन आणि नियम"},
    "tab_risk": {"en": "🎲 Risk lab", "hi": "🎲 जोखिम लैब", "mr": "🎲 जोखीम प्रयोगशाळा"},
    "tab_report": {"en": "🖨 Report", "hi": "🖨 रिपोर्ट", "mr": "🖨 अहवाल"},
    "kpi_gross": {"en": "Expected gross (normal year)", "hi": "अपेक्षित सकल आय (सामान्य साल)", "mr": "अपेक्षित एकूण उत्पन्न (सामान्य वर्ष)"},
    "kpi_net": {"en": "Expected net margin", "hi": "अपेक्षित शुद्ध मार्जिन", "mr": "अपेक्षित निव्वळ नफा"},
    "kpi_peak": {"en": "Busiest week", "hi": "सबसे व्यस्त हफ़्ता", "mr": "सर्वात व्यस्त आठवडा"},
    "wi_title": {"en": "⚡ What-if lab", "hi": "⚡ क्या-हो-अगर लैब", "mr": "⚡ जर-तर प्रयोगशाळा"},
    "wi_help": {"en": "Hit your twin with a shock and replay the season. Your crop allocation stays the same; only the outcome changes.", "hi": "अपने ट्विन पर एक झटका डालें और मौसम दोबारा चलाएँ। फसल बँटवारा वही रहता है; सिर्फ़ नतीजा बदलता है।", "mr": "तुमच्या ट्विनवर एक धक्का द्या आणि हंगाम पुन्हा चालवा. पीक वाटप तेच राहते; फक्त निकाल बदलतो."},
    "wi_kind": {"en": "Shock", "hi": "झटका", "mr": "धक्का"},
    "wi_none": {"en": "None (planned season)", "hi": "कोई नहीं (योजना अनुसार)", "mr": "काही नाही (नियोजनाप्रमाणे)"},
    "wi_dry_spell": {"en": "☀️ Dry spell", "hi": "☀️ सूखा दौर", "mr": "☀️ कोरडा काळ"},
    "wi_pest": {"en": "🐛 Pest attack", "hi": "🐛 कीट हमला", "mr": "🐛 कीड हल्ला"},
    "wi_price": {"en": "📉 Price change", "hi": "📉 भाव बदलाव", "mr": "📉 भाव बदल"},
    "wi_water_cut": {"en": "🚱 Water supply cut", "hi": "🚱 पानी की कटौती", "mr": "🚱 पाणी कपात"},
    "wi_week": {"en": "Starts in week", "hi": "किस हफ़्ते से", "mr": "कोणत्या आठवड्यापासून"},
    "wi_weeks": {"en": "Length (weeks)", "hi": "अवधि (हफ़्ते)", "mr": "कालावधी (आठवडे)"},
    "wi_severity": {"en": "Severity", "hi": "तीव्रता", "mr": "तीव्रता"},
    "wi_crop": {"en": "Crop", "hi": "फसल", "mr": "पीक"},
    "wi_change": {"en": "Price change (%)", "hi": "भाव बदलाव (%)", "mr": "भाव बदल (%)"},
    "wi_water": {"en": "Water left", "hi": "बचा पानी", "mr": "उरलेले पाणी"},
    "wi_apply": {"en": "Apply to twin", "hi": "ट्विन पर लागू करें", "mr": "ट्विनवर लागू करा"},
    "wi_reset": {"en": "Reset", "hi": "रीसेट", "mr": "रीसेट"},
    "wi_impact": {"en": "Season gross revenue under this shock", "hi": "इस झटके में मौसम की सकल आय", "mr": "या धक्क्यात हंगामाचे एकूण उत्पन्न"},
    "wi_vs": {"en": "vs {ref} planned", "hi": "योजना {ref} की तुलना में", "mr": "नियोजित {ref} च्या तुलनेत"},
    "wi_active": {"en": "Active shock: {name}", "hi": "सक्रिय झटका: {name}", "mr": "सक्रिय धक्का: {name}"},
    "wi_note": {"en": "Shock responses are simple prototype assumptions, not crop science.", "hi": "झटकों के असर सरल प्रोटोटाइप मान्यताएँ हैं, फसल विज्ञान नहीं।", "mr": "धक्क्यांचे परिणाम साधी प्रोटोटाइप गृहितके आहेत, पीक विज्ञान नाही."},
    "replan": {"en": "Re-plan for this water", "hi": "इस पानी के लिए नई योजना", "mr": "या पाण्यासाठी नवीन नियोजन"},
    "replan_ok": {"en": "New plan committed for “{water}”. Previous plan: {old}.", "hi": "“{water}” के लिए नई योजना लागू। पिछली योजना: {old}।", "mr": "“{water}” साठी नवीन नियोजन लागू. मागील नियोजन: {old}."},
    "replan_fail": {"en": "No valid plan fits “{water}”, so your current plan is kept.", "hi": "“{water}” में कोई मान्य योजना नहीं, इसलिए मौजूदा योजना रखी गई।", "mr": "“{water}” मध्ये वैध नियोजन नाही, म्हणून सध्याचे नियोजन ठेवले."},
    "replan_hint": {"en": "Your plan needs {used} mm of irrigation but “{water}” allows {limit} mm.", "hi": "आपकी योजना को {used} मिमी सिंचाई चाहिए पर “{water}” में {limit} मिमी है।", "mr": "तुमच्या नियोजनाला {used} मिमी सिंचन लागते पण “{water}” मध्ये {limit} मिमी आहे."},
    "replan_fits": {"en": "Your plan already fits this water level.", "hi": "आपकी योजना इस पानी में पहले से फिट है।", "mr": "तुमचे नियोजन या पाण्यात आधीच बसते."},
    "twin_caption": {"en": "Drag to orbit · scroll to zoom · hover a strip for details. The field is drawn to scale as 20 equal strips; plant shapes are illustrative.", "hi": "घुमाने के लिए खींचें · ज़ूम के लिए स्क्रॉल · जानकारी के लिए पट्टी पर होवर। खेत 20 बराबर पट्टियों में; पौधों के आकार सांकेतिक हैं।", "mr": "फिरवण्यासाठी ओढा · झूमसाठी स्क्रोल · माहितीसाठी पट्ट्यावर होवर. शेत 20 समान पट्ट्यांत; झाडांचे आकार सांकेतिक आहेत."},
    "listening_tip": {"en": "Tip: say district, plot size, season, water source and how much risk you can take.", "hi": "सुझाव: ज़िला, खेत का आकार, मौसम, पानी का स्रोत और जोखिम बताएं।", "mr": "सूचना: जिल्हा, शेताचा आकार, हंगाम, पाण्याचा स्रोत आणि जोखीम सांगा."},
}


def t(key: str, lang: str = "en", **params) -> str:
    entry = T.get(key)
    if entry is None:
        return key
    text = entry.get(lang) or entry["en"]
    return text.format(**params) if params else text


def crop_list(ids, dataset, lang: str) -> str:
    names = []
    for cid in ids:
        if cid in dataset.crops:
            names.append(dataset.crops[cid].name(lang))
        elif cid in dataset.excluded:
            names.append(dataset.excluded[cid].name(lang))
        else:
            names.append(cid)
    return ", ".join(names)


def fmt_acres(acres: float, lang: str) -> str:
    return f"{acres:.2f} {t('unit_acre', lang)}"


def fmt_rs(value: float) -> str:
    """Indian digit grouping, e.g. 1,23,456."""
    neg = value < 0
    s = f"{abs(round(value)):d}"
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    return ("-" if neg else "") + s


def fmt_money(value: float) -> str:
    """₹ amount with a leading minus sign for negatives, e.g. −₹6,877."""
    return ("−₹" if round(value) < 0 else "₹") + fmt_rs(abs(value))


def render_item(item: dict, dataset, lang: str) -> str:
    """Turn an explanation or diagnosis entry from the optimizer into a sentence."""
    key = item["key"]
    p = {k: v for k, v in item.items() if k != "key"}
    if "crops" in p:
        p["crops"] = crop_list(p["crops"], dataset, lang)
    if key == "exp_objective":
        w = p.pop("weight")
        p["pct_mean"], p["pct_cvar"] = round(100 * (1 - w)), round(100 * w)
    elif key == "exp_area":
        p["acres"] = fmt_acres(p["acres"], lang)
        p["strip_acres"] = f"{p['strip_acres']:.3f} {t('unit_acre', lang)}"
    elif key == "exp_water":
        p["binding"] = t("exp_water_binding", lang) if p.pop("binding") else ""
        p["level"] = t(f"water_{p['level']}", lang)
        p["used"], p["limit"] = f"{p['used']:.0f}", f"{p['limit']:.0f}"
    elif key == "exp_budget":
        p["cost"], p["budget"] = fmt_rs(p["cost"]), fmt_rs(p["budget"])
    elif key == "exp_crop":
        p["share"] = f"{p['share']:.0%}"
        p["mean"], p["sd"] = fmt_rs(p["mean"]), fmt_rs(p["sd"])
        p["limit"] = t(f"exp_limit_{p['limit']}", lang) if p["limit"] else ""
    elif key == "exp_shares":
        p["min"], p["max"] = f"{p['min']:.0%}", f"{p['max']:.0%}"
    elif key.startswith("err_"):
        p["field"] = t({"area": "f_area", "region": "f_region", "season": "f_season", "year": "f_year",
                        "water": "f_water", "risk": "f_risk", "budget": "f_budget"}.get(p.get("field"), "f_area"), lang)
    return t(key, lang, **p)
