import xml.etree.ElementTree as ET
import json
import re
import os

# --- PHASE 1: RESEARCHED KNOWLEDGE BASE ---
# This dictionary contains the "intelligence" about philosophers, their categories,
# links, and historical dependencies.
KNOWLEDGE_BASE = {
    # --- Ancient ---
    "presocratics": {"name": "Pre-Socratics", "category": "Ancient", "sep": "https://plato.stanford.edu/entries/presocratics/", "deps": [], "keywords": ["Heraclitus", "Parmenides", "Thales", "Empedocles", "Zeno"]},
    "socrates": {"name": "Socrates", "category": "Ancient", "sep": "https://plato.stanford.edu/entries/socrates/", "deps": ["presocratics"], "keywords": ["Socrates"]},
    "plato": {"name": "Plato", "category": "Ancient", "sep": "https://plato.stanford.edu/entries/plato/", "deps": ["socrates"], "keywords": ["Plato", "Republic", "Symposium", "Phaedo", "Apology", "Euthyphro", "Meno", "Gorgias", "Cratylus", "Sophist", "Theaetetus", "Philebus", "Timaeus", "Laws"]},
    "aristotle": {"name": "Aristotle", "category": "Ancient", "sep": "https://plato.stanford.edu/entries/aristotle/", "deps": ["plato"], "keywords": ["Aristotle", "Nicomachean", "De Anima", "Metaphysics", "Poetics", "Politics"]},
    "stoicism": {"name": "Stoicism", "category": "Ancient", "sep": "https://plato.stanford.edu/entries/stoicism/", "deps": ["socrates"], "keywords": ["Stoic", "Epictetus", "Marcus Aurelius", "Seneca"]},
    "epicureanism": {"name": "Epicureanism", "category": "Ancient", "sep": "https://plato.stanford.edu/entries/epicureanism/", "deps": ["presocratics"], "keywords": ["Epicurus", "Epicurean", "Lucretius"]},
    "skepticism": {"name": "Skepticism", "category": "Ancient", "sep": "https://plato.stanford.edu/entries/skepticism-ancient/", "deps": [], "keywords": ["Sextus Empiricus", "Pyrrho", "Skepticism"]},
    "plotinus": {"name": "Plotinus", "category": "Ancient", "sep": "https://plato.stanford.edu/entries/plotinus/", "deps": ["plato"], "keywords": ["Plotinus", "Neoplatonism"]},

    # --- Medieval & Renaissance ---
    "augustine": {"name": "Augustine", "category": "Medieval", "sep": "https://plato.stanford.edu/entries/augustine/", "deps": ["plato", "plotinus"], "keywords": ["Augustine"]},
    "aquinas": {"name": "Thomas Aquinas", "category": "Medieval", "sep": "https://plato.stanford.edu/entries/aquinas/", "deps": ["aristotle", "augustine"], "keywords": ["Aquinas"]},
    "maimonides": {"name": "Maimonides", "category": "Medieval", "sep": "https://plato.stanford.edu/entries/maimonides/", "deps": ["aristotle"], "keywords": ["Maimonides"]},
    "al-kindi": {"name": "Al-Kindi", "category": "Medieval", "sep": "https://plato.stanford.edu/entries/al-kindi/", "deps": ["aristotle", "plotinus"], "keywords": ["Al-Kindi"]},
    "machiavelli": {"name": "Machiavelli", "category": "Renaissance", "sep": "https://plato.stanford.edu/entries/machiavelli/", "deps": [], "keywords": ["Machiavelli", "The Prince"]},
    "montaigne": {"name": "Montaigne", "category": "Renaissance", "sep": "https://plato.stanford.edu/entries/montaigne/", "deps": ["skepticism"], "keywords": ["Montaigne"]},
    "ficino": {"name": "Marsilio Ficino", "category": "Renaissance", "sep": "https://plato.stanford.edu/entries/ficino/", "deps": ["plato", "plotinus"], "keywords": ["Ficino"]},
    "erasmus": {"name": "Erasmus", "category": "Renaissance", "sep": "https://plato.stanford.edu/entries/erasmus/", "deps": [], "keywords": ["Erasmus"]},

    # --- Modern (17th-18th C) ---
    "hobbes": {"name": "Thomas Hobbes", "category": "Modern", "sep": "https://plato.stanford.edu/entries/hobbes/", "deps": ["machiavelli"], "keywords": ["Hobbes", "Leviathan"]},
    "descartes": {"name": "René Descartes", "category": "Modern", "sep": "https://plato.stanford.edu/entries/descartes/", "deps": ["augustine", "skepticism"], "keywords": ["Descartes", "Meditations"]},
    "spinoza": {"name": "Baruch Spinoza", "category": "Modern", "sep": "https://plato.stanford.edu/entries/spinoza/", "deps": ["descartes", "hobbes"], "keywords": ["Spinoza"]},
    "leibniz": {"name": "Gottfried Leibniz", "category": "Modern", "sep": "https://plato.stanford.edu/entries/leibniz/", "deps": ["descartes", "spinoza"], "keywords": ["Leibniz", "Monadology"]},
    "malebranche": {"name": "Nicolas Malebranche", "category": "Modern", "sep": "https://plato.stanford.edu/entries/malebranche/", "deps": ["descartes", "augustine"], "keywords": ["Malebranche"]},
    "pascal": {"name": "Blaise Pascal", "category": "Modern", "sep": "https://plato.stanford.edu/entries/pascal/", "deps": ["montaigne", "descartes"], "keywords": ["Pascal"]},
    "locke": {"name": "John Locke", "category": "Modern", "sep": "https://plato.stanford.edu/entries/locke/", "deps": ["descartes", "hobbes"], "keywords": ["Locke"]},
    "berkeley": {"name": "George Berkeley", "category": "Modern", "sep": "https://plato.stanford.edu/entries/berkeley/", "deps": ["locke"], "keywords": ["Berkeley"]},
    "hume": {"name": "David Hume", "category": "Modern", "sep": "https://plato.stanford.edu/entries/hume/", "deps": ["locke", "berkeley", "hutcheson"], "keywords": ["Hume"]},
    "smith": {"name": "Adam Smith", "category": "Modern", "sep": "https://plato.stanford.edu/entries/smith-moral-political/", "deps": ["hume"], "keywords": ["Adam Smith"]},
    "rousseau": {"name": "Jean-Jacques Rousseau", "category": "Modern", "sep": "https://plato.stanford.edu/entries/rousseau/", "deps": ["hobbes", "locke"], "keywords": ["Rousseau"]},
    "kant": {"name": "Immanuel Kant", "category": "Modern", "sep": "https://plato.stanford.edu/entries/kant/", "deps": ["hume", "leibniz", "rousseau"], "keywords": ["Kant", "Critique"]},
    "burke": {"name": "Edmund Burke", "category": "Modern", "sep": "https://plato.stanford.edu/entries/burke/", "deps": ["locke"], "keywords": ["Burke"]},
    "reid": {"name": "Thomas Reid", "category": "Modern", "sep": "https://plato.stanford.edu/entries/reid/", "deps": ["hume", "locke"], "keywords": ["Reid"]},

    # --- 19th Century ---
    "hegel": {"name": "G.W.F. Hegel", "category": "19th Century", "sep": "https://plato.stanford.edu/entries/hegel/", "deps": ["kant", "fichte", "schelling"], "keywords": ["Hegel", "Phenomenology"]},
    "fichte": {"name": "J.G. Fichte", "category": "19th Century", "sep": "https://plato.stanford.edu/entries/johann-fichte/", "deps": ["kant"], "keywords": ["Fichte"]},
    "schelling": {"name": "F.W.J. Schelling", "category": "19th Century", "sep": "https://plato.stanford.edu/entries/schelling/", "deps": ["kant", "fichte", "spinoza"], "keywords": ["Schelling"]},
    "schopenhauer": {"name": "Arthur Schopenhauer", "category": "19th Century", "sep": "https://plato.stanford.edu/entries/schopenhauer/", "deps": ["kant", "plato"], "keywords": ["Schopenhauer"]},
    "kierkegaard": {"name": "Søren Kierkegaard", "category": "19th Century", "sep": "https://plato.stanford.edu/entries/kierkegaard/", "deps": ["hegel", "socrates"], "keywords": ["Kierkegaard", "Fear and Trembling", "Sickness Unto Death", "Either/Or"]},
    "marx": {"name": "Karl Marx", "category": "19th Century", "sep": "https://plato.stanford.edu/entries/marx/", "deps": ["hegel", "feuerbach", "smith"], "keywords": ["Marx", "Communist", "Capital"]},
    "stirner": {"name": "Max Stirner", "category": "19th Century", "sep": "https://plato.stanford.edu/entries/max-stirner/", "deps": ["hegel", "feuerbach"], "keywords": ["Stirner"]},
    "feuerbach": {"name": "Ludwig Feuerbach", "category": "19th Century", "sep": "https://plato.stanford.edu/entries/ludwig-feuerbach/", "deps": ["hegel"], "keywords": ["Feuerbach"]},
    "nietzsche": {"name": "Friedrich Nietzsche", "category": "19th Century", "sep": "https://plato.stanford.edu/entries/nietzsche/", "deps": ["schopenhauer", "wagner", "presocratics"], "keywords": ["Nietzsche", "Zarathustra", "Beyond Good and Evil", "Gay Science"]},
    "mill": {"name": "J.S. Mill", "category": "19th Century", "sep": "https://plato.stanford.edu/entries/mill/", "deps": ["bentham", "aristotle"], "keywords": ["Mill", "Utilitarianism"]},
    "bentham": {"name": "Jeremy Bentham", "category": "19th Century", "sep": "https://plato.stanford.edu/entries/bentham/", "deps": ["hume"], "keywords": ["Bentham"]},
    "emerson": {"name": "Ralph Waldo Emerson", "category": "19th Century", "sep": "https://plato.stanford.edu/entries/emerson/", "deps": ["plato", "kant"], "keywords": ["Emerson", "Oversoul"]},
    "thoreau": {"name": "Henry David Thoreau", "category": "19th Century", "sep": "https://plato.stanford.edu/entries/thoreau/", "deps": ["emerson"], "keywords": ["Thoreau"]},

    # --- 20th Century / Continental ---
    "husserl": {"name": "Edmund Husserl", "category": "Phenomenology", "sep": "https://plato.stanford.edu/entries/husserl/", "deps": ["brentano", "descartes", "kant"], "keywords": ["Husserl"]},
    "heidegger": {"name": "Martin Heidegger", "category": "Phenomenology", "sep": "https://plato.stanford.edu/entries/heidegger/", "deps": ["husserl", "aristotle", "nietzsche"], "keywords": ["Heidegger", "Being and Time"]},
    "sartre": {"name": "Jean-Paul Sartre", "category": "Existentialism", "sep": "https://plato.stanford.edu/entries/sartre/", "deps": ["heidegger", "husserl", "kierkegaard", "marx"], "keywords": ["Sartre", "No Exit", "Being and Nothingness"]},
    "camus": {"name": "Albert Camus", "category": "Existentialism", "sep": "https://plato.stanford.edu/entries/camus/", "deps": ["sartre", "nietzsche"], "keywords": ["Camus", "The Stranger", "Myth of Sisyphus"]},
    "beauvoir": {"name": "Simone de Beauvoir", "category": "Existentialism", "sep": "https://plato.stanford.edu/entries/beauvoir/", "deps": ["sartre", "hegel"], "keywords": ["Beauvoir", "Second Sex"]},
    "merleau_ponty": {"name": "Maurice Merleau-Ponty", "category": "Phenomenology", "sep": "https://plato.stanford.edu/entries/merleau-ponty/", "deps": ["husserl", "heidegger"], "keywords": ["Merleau-Ponty"]},
    "levinas": {"name": "Emmanuel Levinas", "category": "Phenomenology", "sep": "https://plato.stanford.edu/entries/levinas/", "deps": ["husserl", "heidegger"], "keywords": ["Levinas"]},
    "arendt": {"name": "Hannah Arendt", "category": "Political Phil", "sep": "https://plato.stanford.edu/entries/arendt/", "deps": ["heidegger", "jaspers", "kant"], "keywords": ["Arendt"]},
    "foucault": {"name": "Michel Foucault", "category": "Post-Structuralism", "sep": "https://plato.stanford.edu/entries/foucault/", "deps": ["nietzsche", "heidegger", "marx"], "keywords": ["Foucault"]},
    "derrida": {"name": "Jacques Derrida", "category": "Post-Structuralism", "sep": "https://plato.stanford.edu/entries/derrida/", "deps": ["heidegger", "husserl", "saussure"], "keywords": ["Derrida"]},
    "deleuze": {"name": "Gilles Deleuze", "category": "Post-Structuralism", "sep": "https://plato.stanford.edu/entries/deleuze/", "deps": ["nietzsche", "spinoza", "bergson"], "keywords": ["Deleuze"]},
    "badiou": {"name": "Alain Badiou", "category": "Continental", "sep": "https://plato.stanford.edu/entries/badiou/", "deps": ["sartre", "lacan", "marx"], "keywords": ["Badiou"]},
    "lacan": {"name": "Jacques Lacan", "category": "Psychoanalysis", "sep": "https://plato.stanford.edu/entries/lacan/", "deps": ["freud", "hegel"], "keywords": ["Lacan"]},
    "habermas": {"name": "Jürgen Habermas", "category": "Critical Theory", "sep": "https://plato.stanford.edu/entries/habermas/", "deps": ["adorno", "horkheimer", "kant"], "keywords": ["Habermas"]},
    "adorno_horkheimer": {"name": "Adorno & Horkheimer", "category": "Critical Theory", "sep": "https://plato.stanford.edu/entries/critical-theory/", "deps": ["marx", "kant", "hegel", "freud"], "keywords": ["Adorno", "Horkheimer", "Dialectic of Enlightenment"]},

    # --- Analytic / Pragmatism ---
    "frege": {"name": "Gottlob Frege", "category": "Analytic", "sep": "https://plato.stanford.edu/entries/frege/", "deps": ["kant", "leibniz"], "keywords": ["Frege"]},
    "russell": {"name": "Bertrand Russell", "category": "Analytic", "sep": "https://plato.stanford.edu/entries/russell/", "deps": ["leibniz", "frege", "moore"], "keywords": ["Russell"]},
    "wittgenstein": {"name": "Ludwig Wittgenstein", "category": "Analytic", "sep": "https://plato.stanford.edu/entries/wittgenstein/", "deps": ["frege", "russell"], "keywords": ["Wittgenstein", "Tractatus", "Philosophical Investigations", "On Certainty"]},
    "moore": {"name": "G.E. Moore", "category": "Analytic", "sep": "https://plato.stanford.edu/entries/moore/", "deps": [], "keywords": ["G.E. Moore", "Common Sense"]},
    "quine": {"name": "W.V.O. Quine", "category": "Analytic", "sep": "https://plato.stanford.edu/entries/quine/", "deps": ["carnap", "russell"], "keywords": ["Quine"]},
    "kuhn": {"name": "Thomas Kuhn", "category": "Phil of Science", "sep": "https://plato.stanford.edu/entries/thomas-kuhn/", "deps": ["popper"], "keywords": ["Kuhn", "Scientific Revolutions"]},
    "popper": {"name": "Karl Popper", "category": "Phil of Science", "sep": "https://plato.stanford.edu/entries/popper/", "deps": ["hume", "kant"], "keywords": ["Popper"]},
    "lakatos": {"name": "Imre Lakatos", "category": "Phil of Science", "sep": "https://plato.stanford.edu/entries/lakatos/", "deps": ["popper", "kuhn"], "keywords": ["Lakatos"]},
    "feyerabend": {"name": "Paul Feyerabend", "category": "Phil of Science", "sep": "https://plato.stanford.edu/entries/feyerabend/", "deps": ["kuhn", "lakatos"], "keywords": ["Feyerabend", "Against Method"]},
    "james": {"name": "William James", "category": "Pragmatism", "sep": "https://plato.stanford.edu/entries/james/", "deps": ["peirce", "mill"], "keywords": ["William James", "Pragmatism"]},
    "dewey": {"name": "John Dewey", "category": "Pragmatism", "sep": "https://plato.stanford.edu/entries/dewey/", "deps": ["james", "hegel"], "keywords": ["Dewey"]},
    "rorty": {"name": "Richard Rorty", "category": "Pragmatism", "sep": "https://plato.stanford.edu/entries/rorty/", "deps": ["dewey", "wittgenstein", "heidegger"], "keywords": ["Rorty"]},
    "rawls": {"name": "John Rawls", "category": "Political Phil", "sep": "https://plato.stanford.edu/entries/rawls/", "deps": ["kant", "locke", "rousseau"], "keywords": ["Rawls", "Theory of Justice"]},
    "nozick": {"name": "Robert Nozick", "category": "Political Phil", "sep": "https://plato.stanford.edu/entries/nozick-political/", "deps": ["locke", "rawls"], "keywords": ["Nozick", "Anarchy"]},
    "parfit": {"name": "Derek Parfit", "category": "Ethics", "sep": "https://plato.stanford.edu/entries/parfit/", "deps": ["sidgwick", "kant"], "keywords": ["Parfit"]},
    "foot": {"name": "Philippa Foot", "category": "Ethics", "sep": "https://plato.stanford.edu/entries/foot-philippa/", "deps": ["aristotle", "aquinas"], "keywords": ["Philippa Foot"]},
    "korsgaard": {"name": "Christine Korsgaard", "category": "Ethics", "sep": "https://plato.stanford.edu/entries/kant-moral/", "deps": ["kant", "rawls"], "keywords": ["Korsgaard"]},
    "railton": {"name": "Peter Railton", "category": "Ethics", "sep": "https://plato.stanford.edu/entries/naturalism-moral/", "deps": ["hume"], "keywords": ["Railton", "Moral Realism"]},
    "williamson": {"name": "Timothy Williamson", "category": "Analytic", "sep": "", "deps": [], "keywords": ["Williamson"]},
    "chalmers": {"name": "David Chalmers", "category": "Phil of Mind", "sep": "https://plato.stanford.edu/entries/chalmers/", "deps": ["descartes"], "keywords": ["Chalmers"]},
    "dennett": {"name": "Daniel Dennett", "category": "Phil of Mind", "sep": "https://plato.stanford.edu/entries/dennett/", "deps": ["quine", "ryle"], "keywords": ["Dennett"]},
    "searle": {"name": "John Searle", "category": "Phil of Mind", "sep": "https://plato.stanford.edu/entries/searle/", "deps": ["austin"], "keywords": ["Searle"]},

    # --- Eastern ---
    "confucius": {"name": "Confucius", "category": "Eastern", "sep": "https://plato.stanford.edu/entries/confucius/", "deps": [], "keywords": ["Confucius", "Analects"]},
    "mencius": {"name": "Mengzi (Mencius)", "category": "Eastern", "sep": "https://plato.stanford.edu/entries/mencius/", "deps": ["confucius"], "keywords": ["Mengzi", "Mencius"]},
    "mozi": {"name": "Mozi", "category": "Eastern", "sep": "https://plato.stanford.edu/entries/mohism/", "deps": ["confucius"], "keywords": ["Mozi", "Mohism"]},
    "laozi": {"name": "Laozi", "category": "Eastern", "sep": "https://plato.stanford.edu/entries/laozi/", "deps": [], "keywords": ["Laozi", "Dao De Jing", "Daodejing", "Dao"]},
    "zhuangzi": {"name": "Zhuangzi", "category": "Eastern", "sep": "https://plato.stanford.edu/entries/zhuangzi/", "deps": ["laozi"], "keywords": ["Zhuangzi"]},
    "nyaya": {"name": "Nyaya", "category": "Eastern", "sep": "https://plato.stanford.edu/entries/epistemology-india/", "deps": [], "keywords": ["Nyaya"]},
    "nagarjuna": {"name": "Nagarjuna", "category": "Eastern", "sep": "https://plato.stanford.edu/entries/nagarjuna/", "deps": [], "keywords": ["Nagarjuna"]},
    "gita": {"name": "Bhagavad Gita", "category": "Eastern", "sep": "", "deps": [], "keywords": ["Bhagavad Gita", "Gita"]},

    # --- Others/Topics ---
    "liberalism": {"name": "Liberalism", "category": "Topic", "sep": "https://plato.stanford.edu/entries/liberalism/", "deps": ["locke", "mill", "rawls"], "keywords": ["Liberalism"]},
    "abortion": {"name": "Abortion Ethics", "category": "Topic", "sep": "https://plato.stanford.edu/entries/abortion/", "deps": ["foot", "thomson"], "keywords": ["Abortion"]},
    "terrorism": {"name": "Terrorism", "category": "Topic", "sep": "https://plato.stanford.edu/entries/terrorism/", "deps": [], "keywords": ["Terrorism"]},
    "freud": {"name": "Sigmund Freud", "category": "Psychoanalysis", "sep": "https://plato.stanford.edu/entries/freud/", "deps": ["nietzsche"], "keywords": ["Freud"]},
    "jung": {"name": "Carl Jung", "category": "Psychoanalysis", "sep": "", "deps": ["freud"], "keywords": ["Jung"]},
    "brentano": {"name": "Franz Brentano", "category": "Phenomenology", "sep": "https://plato.stanford.edu/entries/brentano/", "deps": ["aristotle"], "keywords": ["Brentano"]},
    "stein": {"name": "Edith Stein", "category": "Phenomenology", "sep": "https://plato.stanford.edu/entries/stein/", "deps": ["husserl"], "keywords": ["Edith Stein"]},
    "scheler": {"name": "Max Scheler", "category": "Phenomenology", "sep": "https://plato.stanford.edu/entries/scheler/", "deps": ["husserl", "nietzsche"], "keywords": ["Scheler"]},
    "buber": {"name": "Martin Buber", "category": "Existentialism", "sep": "https://plato.stanford.edu/entries/buber/", "deps": ["kierkegaard"], "keywords": ["Buber", "I and Thou"]},
    "weil": {"name": "Simone Weil", "category": "Modern", "sep": "https://plato.stanford.edu/entries/simone-weil/", "deps": ["plato", "marx", "kant"], "keywords": ["Simone Weil"]},
    "cioran": {"name": "Emil Cioran", "category": "Existentialism", "sep": "", "deps": ["nietzsche", "schopenhauer"], "keywords": ["Cioran"]},
    "tomasello": {"name": "Michael Tomasello", "category": "Phil of Mind", "sep": "", "deps": [], "keywords": ["Tomasello"]},
    "haraway": {"name": "Donna Haraway", "category": "Feminist Phil", "sep": "https://plato.stanford.edu/entries/feminist-science/", "deps": ["foucault"], "keywords": ["Haraway"]},
    "irigaray": {"name": "Luce Irigaray", "category": "Feminist Phil", "sep": "https://plato.stanford.edu/entries/irigaray/", "deps": ["lacan", "derrida", "beauvoir"], "keywords": ["Irigaray"]},
    "butler": {"name": "Judith Butler", "category": "Feminist Phil", "sep": "https://plato.stanford.edu/entries/feminist-body/", "deps": ["foucault", "derrida"], "keywords": ["Judith Butler"]},
    "scruton": {"name": "Roger Scruton", "category": "Aesthetics", "sep": "https://plato.stanford.edu/entries/aesthetic-judgment/", "deps": ["kant", "burke"], "keywords": ["Scruton"]},
    "langer": {"name": "Susanne Langer", "category": "Aesthetics", "sep": "https://plato.stanford.edu/entries/langer/", "deps": ["cassirer", "whitehead"], "keywords": ["Langer"]},
    "cassirer": {"name": "Ernst Cassirer", "category": "Neo-Kantian", "sep": "https://plato.stanford.edu/entries/cassirer/", "deps": ["kant"], "keywords": ["Cassirer"]},
    "dostoevsky": {"name": "Fyodor Dostoevsky", "category": "Literature", "sep": "https://plato.stanford.edu/entries/dostoevsky/", "deps": ["existentialism"], "keywords": ["Dostoevsky", "Brothers Karamazov"]},
    "shakespeare": {"name": "William Shakespeare", "category": "Literature", "sep": "", "deps": [], "keywords": ["Shakespeare", "Timon of Athens"]},
    "mccarthy": {"name": "Cormac McCarthy", "category": "Literature", "sep": "", "deps": [], "keywords": ["Cormac McCarthy", "Blood Meridian"]},
    "thoreau": {"name": "Henry David Thoreau", "category": "19th Century", "sep": "https://plato.stanford.edu/entries/thoreau/", "deps": ["emerson"], "keywords": ["Thoreau"]},
    "royce": {"name": "Josiah Royce", "category": "Pragmatism", "sep": "https://plato.stanford.edu/entries/royce/", "deps": ["hegel", "james"], "keywords": ["Royce"]},
    "grice": {"name": "Paul Grice", "category": "Analytic", "sep": "https://plato.stanford.edu/entries/grice/", "deps": ["austin", "wittgenstein"], "keywords": ["Grice"]},
    "austin": {"name": "J.L. Austin", "category": "Analytic", "sep": "https://plato.stanford.edu/entries/austin/", "deps": [], "keywords": ["J.L. Austin"]},
    "strawson": {"name": "P.F. Strawson", "category": "Analytic", "sep": "https://plato.stanford.edu/entries/strawson/", "deps": ["kant", "wittgenstein"], "keywords": ["P.F. Strawson"]},
    "frankfurt": {"name": "Harry Frankfurt", "category": "Analytic", "sep": "https://plato.stanford.edu/entries/compatibilism/", "deps": [], "keywords": ["Harry Frankfurt", "Bullshit"]},
    "bergson": {"name": "Henri Bergson", "category": "Process Phil", "sep": "https://plato.stanford.edu/entries/bergson/", "deps": [], "keywords": ["Bergson"]},
    "whitehead": {"name": "Alfred North Whitehead", "category": "Process Phil", "sep": "https://plato.stanford.edu/entries/whitehead/", "deps": [], "keywords": ["Whitehead"]},
    "santayana": {"name": "George Santayana", "category": "Naturalism", "sep": "https://plato.stanford.edu/entries/santayana/", "deps": ["spinoza", "james"], "keywords": ["Santayana"]},
    "mounk": {"name": "Yascha Mounk", "category": "Political Phil", "sep": "", "deps": ["liberalism"], "keywords": ["Yascha Mounk", "Identity Trap"]},
    "sandel": {"name": "Michael Sandel", "category": "Political Phil", "sep": "https://plato.stanford.edu/entries/communitarianism/", "deps": ["rawls", "aristotle"], "keywords": ["Sandel"]},
    "badiou": {"name": "Alain Badiou", "category": "Continental", "sep": "https://plato.stanford.edu/entries/badiou/", "deps": ["sartre", "lacan", "marx"], "keywords": ["Badiou"]},
    "agamben": {"name": "Giorgio Agamben", "category": "Continental", "sep": "", "deps": ["heidegger", "benjamin"], "keywords": ["Agamben"]},
    "benjamin": {"name": "Walter Benjamin", "category": "Critical Theory", "sep": "https://plato.stanford.edu/entries/benjamin/", "deps": ["marx"], "keywords": ["Benjamin"]},
}

# Add a default "uncategorized" key for unmatched items
KNOWLEDGE_BASE["uncategorized"] = {"name": "Uncategorized", "category": "Other", "sep": None, "deps": [], "keywords": []}

def normalize(text):
    return text.lower() if text else ""

def parse_rss_feed(filename):
    """Parses the RSS XML and extracts episodes."""
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return []

    episodes = []
    # Namespaces can be tricky. Usually items are in channel/item.
    # We will try a few paths.
    items = root.findall('.//item')
    
    print(f"Found {len(items)} items in XML.")

    for item in items:
        title = item.find('title').text if item.find('title') is not None else "No Title"
        link = item.find('link').text if item.find('link') is not None else "#"
        # Optional: Parse description for more keywords if needed, but title is usually enough for PEL
        episodes.append({'title': title, 'link': link})
    
    return episodes

def categorize_episodes(episodes, db):
    """Maps episodes to the Knowledge Base."""
    
    # Initialize the output structure
    output_data = {}
    for key, info in db.items():
        if key == "uncategorized": continue
        output_data[key] = {
            "id": key,
            "name": info['name'],
            "category": info['category'],
            "sep_link": info['sep'],
            "dependencies": info['deps'],
            "episodes": []
        }
    
    unmapped = []
    mapped_count = 0

    for ep in episodes:
        title_lower = normalize(ep['title'])
        matched = False
        
        # Check against every philosopher in the DB
        for key, info in db.items():
            if key == "uncategorized": continue
            for keyword in info['keywords']:
                # Simple keyword matching: checks if keyword is in title
                if normalize(keyword) in title_lower:
                    output_data[key]['episodes'].append(ep)
                    matched = True
                    break # Stop checking keywords for this philosopher
            if matched: break # Stop checking philosophers for this episode (primary match)
        
        if not matched:
            # Try to catch some common variations or generic topics if not in DB
            # For now, add to unmapped
            unmapped.append(ep)
        else:
            mapped_count += 1
            
    # Remove empty nodes (philosophers with no episodes) to keep the graph clean?
    # Or keep them if they are dependencies? 
    # Better to keep them if they are dependencies of active nodes, but for now let's keep only nodes with episodes OR valid dependencies
    # To simplify, we will keep all nodes that have episodes, plus any nodes that are listed as dependencies of those nodes.
    
    active_keys = set()
    for key, data in output_data.items():
        if data['episodes']:
            active_keys.add(key)
            for dep in data['dependencies']:
                if dep in db: # Only add if it exists in our DB
                    active_keys.add(dep)
    
    final_json = []
    for key in active_keys:
        # For dependency-only nodes (no episodes found), ensure they exist in structure
        if key not in output_data:
             # This happens if a dependency is in DB but didn't have its own entry init (shouldn't happen with code above)
             pass
        final_json.append(output_data[key])

    # Report
    print(f"Total Episodes Processed: {len(episodes)}")
    print(f"Successfully Mapped: {mapped_count}")
    print(f"Unmapped: {len(unmapped)}")
    
    if len(unmapped) > 0:
        print("\n--- Unmapped Episodes (First 10) ---")
        for ep in unmapped[:10]:
            print(ep['title'])
            
    return final_json

def generate_html(json_data):
    """Generates the Single Page App."""
    
    json_str = json.dumps(json_data, indent=2)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Philosophy Podcast Mind Map</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #1a1a1a; color: #f0f0f0; margin: 0; overflow: hidden; }}
        #container {{ display: flex; height: 100vh; }}
        #sidebar {{ width: 350px; background-color: #2c2c2c; padding: 20px; box-shadow: 2px 0 5px rgba(0,0,0,0.5); overflow-y: auto; z-index: 10; }}
        #graph-area {{ flex-grow: 1; position: relative; }}
        
        h1 {{ font-size: 1.2em; color: #61dafb; margin-top: 0; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid #444; padding-bottom: 10px; }}
        
        .episode-link {{ display: block; margin: 5px 0; color: #ddd; text-decoration: none; padding: 5px; background: #3a3a3a; border-radius: 4px; }}
        .episode-link:hover {{ background: #505050; color: #fff; }}
        
        .sep-link {{ display: inline-block; margin-top: 10px; color: #ff6b6b; font-weight: bold; text-decoration: none; }}
        .sep-link:hover {{ text-decoration: underline; }}

        .search-container {{ margin-bottom: 20px; }}
        input[type="text"] {{ width: 100%; padding: 10px; border-radius: 4px; border: none; background: #444; color: white; }}
        
        .node circle {{ stroke: #fff; stroke-width: 1.5px; cursor: pointer; transition: all 0.3s; }}
        .node:hover circle {{ stroke: #61dafb; stroke-width: 3px; r: 25 !important; }}
        .node text {{ font: 10px sans-serif; pointer-events: none; fill: #eee; text-shadow: 1px 1px 2px #000; }}
        
        .link {{ fill: none; stroke: #555; stroke-opacity: 0.6; marker-end: url(#arrow); }}
        
        /* Category Colors */
        .cat-Ancient {{ fill: #ff9f43; }}
        .cat-Medieval {{ fill: #feca57; }}
        .cat-Modern {{ fill: #ff6b6b; }}
        .cat-19th_Century {{ fill: #ff9ff3; }}
        .cat-Analytic {{ fill: #54a0ff; }}
        .cat-Continental {{ fill: #00d2d3; }}
        .cat-Phenomenology {{ fill: #1dd1a1; }}
        .cat-Existentialism {{ fill: #10ac84; }}
        .cat-Eastern {{ fill: #5f27cd; }}
        .cat-Topic {{ fill: #c8d6e5; }}
        .cat-Literature {{ fill: #8395a7; }}

        #dependency-list {{ margin-top: 15px; font-size: 0.9em; color: #aaa; }}
        .dep-item {{ color: #61dafb; cursor: pointer; }}
    </style>
</head>
<body>

<div id="container">
    <div id="sidebar">
        <h1>PEL Mind Map</h1>
        <div class="search-container">
            <input type="text" id="search" placeholder="Search philosopher or topic...">
        </div>
        <div id="details">
            <p><i>Click a node to view episodes and details.</i></p>
        </div>
    </div>
    <div id="graph-area"></div>
</div>

<script>
    // --- Data Injection ---
    const rawData = {json_str};

    // --- Process Data for D3 ---
    // We need nodes and links.
    // Nodes: The objects in rawData.
    // Links: Created from 'dependencies'.

    const nodes = rawData.map(d => ({{ ...d }}));
    const links = [];
    const nodeMap = new Map(nodes.map(n => [n.id, n]));

    nodes.forEach(sourceNode => {{
        if (sourceNode.dependencies) {{
            sourceNode.dependencies.forEach(targetId => {{
                if (nodeMap.has(targetId)) {{
                    links.push({{ source: sourceNode.id, target: targetId }});
                }}
            }});
        }}
    }});

    // --- D3 Visualization ---
    const width = document.getElementById('graph-area').clientWidth;
    const height = document.getElementById('graph-area').clientHeight;

    const svg = d3.select("#graph-area").append("svg")
        .attr("width", width)
        .attr("height", height)
        .call(d3.zoom().on("zoom", (event) => {{
            g.attr("transform", event.transform);
        }}));

    const g = svg.append("g");

    // Arrowhead marker
    svg.append("defs").selectAll("marker")
        .data(["arrow"])
        .enter().append("marker")
        .attr("id", d => d)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 25) // Position of arrow relative to node center
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", "#555");

    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-400))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collide", d3.forceCollide(30));

    const link = g.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("class", "link");

    const node = g.append("g")
        .attr("class", "nodes")
        .selectAll("g")
        .data(nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    node.append("circle")
        .attr("r", d => 5 + (d.episodes.length * 1.5)) // Size based on episode count
        .attr("class", d => "cat-" + d.category.replace(/ /g, "_").replace(/&/g,""));

    node.append("text")
        .attr("dy", -10)
        .attr("text-anchor", "middle")
        .text(d => d.name);

    // --- Interaction ---
    node.on("click", (event, d) => {{
        showDetails(d);
    }});

    function showDetails(d) {{
        const details = document.getElementById("details");
        let html = `<h2>${{d.name}}</h2>`;
        html += `<p><span style="color:#aaa;">Category:</span> ${{d.category}}</p>`;
        
        if (d.sep_link) {{
            html += `<a href="${{d.sep_link}}" target="_blank" class="sep-link">Stanford Encyclopedia Entry</a>`;
        }}

        if (d.dependencies && d.dependencies.length > 0) {{
            html += `<div id="dependency-list"><strong>Prerequisites/Influences:</strong><br>`;
            d.dependencies.forEach(depId => {{
                const depName = nodeMap.get(depId) ? nodeMap.get(depId).name : depId;
                html += `<span class="dep-item" onclick="clickNode('${{depId}}')">${{depName}}</span>; `;
            }});
            html += `</div>`;
        }}

        html += `<h3>Episodes (${{d.episodes.length}})</h3>`;
        d.episodes.forEach(ep => {{
            html += `<a href="${{ep.link}}" target="_blank" class="episode-link">${{ep.title}}</a>`;
        }});

        details.innerHTML = html;
    }}
    
    // Allow clicking dependencies in sidebar to jump to node
    window.clickNode = function(id) {{
        const target = nodes.find(n => n.id === id);
        if (target) showDetails(target);
    }};

    // --- Search ---
    document.getElementById("search").addEventListener("input", function(e) {{
        const term = e.target.value.toLowerCase();
        node.style("opacity", d => d.name.toLowerCase().includes(term) ? 1 : 0.1);
        link.style("opacity", d => (d.source.name.toLowerCase().includes(term) || d.target.name.toLowerCase().includes(term)) ? 1 : 0.1);
    }});

    // --- Simulation Update ---
    simulation.on("tick", () => {{
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("transform", d => `translate(${{d.x}},${{d.y}})`);
    }});

    function dragstarted(event, d) {{
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }}

    function dragged(event, d) {{
        d.fx = event.x;
        d.fy = event.y;
    }}

    function dragended(event, d) {{
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }}
</script>

</body>
</html>
"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Successfully created index.html")

# --- Main Execution ---
if __name__ == "__main__":
    file_name = "pel.xml"
    if not os.path.exists(file_name):
        print(f"Error: {file_name} not found. Please verify the file path.")
    else:
        episodes = parse_rss_feed(file_name)
        if episodes:
            final_data = categorize_episodes(episodes, KNOWLEDGE_BASE)
            generate_html(final_data)
        else:
            print("No episodes found in XML.")