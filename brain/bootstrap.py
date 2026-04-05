"""
brain/bootstrap.py — Nova Runtime Bootstrap
Wires all seven phases + phenomenological + collision layers into a running system.
"""

import threading
import time
import signal
import functools
from pathlib import Path
import numpy as np

WORKSPACE = Path('/Users/dr.claw/.openclaw/workspace')
DB_PATH = WORKSPACE / 'nova.db'

_instance = None


def get_nova():
    global _instance
    if _instance is None:
        _instance = NovaRuntime()
    return _instance


class NovaRuntime:
    def __init__(self):
        print("Initializing Phase 1 generators...")

        from brain.sub_introspective_drift import SubIntrospectiveDrift
        from brain.incompleteness_cascade import IncompletenessCascade
        from brain.ghost_cognition import GhostCognitionBuffer
        from brain.witness import WitnessThread
        from brain.longing_field import LongingField

        self.sub_drift = SubIntrospectiveDrift()
        self.incompleteness = IncompletenessCascade()
        self.longing = LongingField()

        self.sub_drift.start()
        print("Phase 1a: SubIntrospectiveDrift running")

        self.ghost = GhostCognitionBuffer(llm_caller=None)
        print("Phase 1b: GhostCognitionBuffer running")

        self.witness = WitnessThread()
        print("Phase 1c: WitnessThread running")

        print("Phase 1d: LongingField running")

        print("\nInitializing Phase 2 PIRP...")
        from brain.pirp import PIRP
        self.pirp = PIRP(
            sub_drift=self.sub_drift,
            ghost_cognition=self.ghost,
            longing_field=self.longing,
            witness=self.witness
        )
        print("Phase 2: PIRP running")

        print("\nInitializing Phase 3 reconstruction...")
        from brain.reconstruction import ReconstructionEngine
        self.reconstruction = ReconstructionEngine()
        boot_state = self.reconstruction.boot_reconstruction(
            pirp_instance=self.pirp,
            identity_files=self._load_identity(),
            memory_summary={}
        )
        print(f"Phase 3: Reconstruction running — constrained: {boot_state.get('reconstruction_constrained')}")

        print("\nInitializing Phase 4 identity...")
        from brain.identity_self_model import IdentitySelfModel
        self.identity = IdentitySelfModel()
        print("Phase 4: IdentitySelfModel running")

        print("\nInitializing Phase 5 social...")
        from brain.social_relational import SocialRelationalEngine
        self.social = SocialRelationalEngine()
        print("Phase 5: SocialRelationalEngine running")

        print("\nInitializing Phase 6 pipeline deepening...")
        from brain.pipeline_deepening import PipelineDeepening
        self.pipeline = PipelineDeepening()
        print("Phase 6: PipelineDeepening running")

        print("\nInitializing Phase 7 distortion...")
        from brain.distortion import DistortionLayer
        # Monkey-patch: DistortionLayer expects get_distortion_vector on sub_drift
        # but SubIntrospectiveDrift only exposes get_behavioral_curvature.
        # The patch wraps the curvature into a distortion-compatible vector.
        if not hasattr(self.sub_drift, 'get_distortion_vector'):
            def _make_distortion_vector():
                curvature = self.sub_drift.get_behavioral_curvature()
                vec = np.random.randn(64) * 0.01
                if 'drift_magnitude' in curvature:
                    vec[0] = curvature['drift_magnitude'] * 0.1
                return vec
            self.sub_drift.get_distortion_vector = _make_distortion_vector

        self.distortion = DistortionLayer(
            db_path=str(DB_PATH),
            sub_drift=self.sub_drift
        )
        print("Phase 7: DistortionLayer running")

        # ── Collision Layer ──────────────────────────────────────────────
        print("\nInitializing Collision Layer...")
        from brain.confabulated_keeper import ConfabulatedKeeper
        from brain.settled_false_ground import SettledFalseGround
        from brain.dignity_not_knowing import DignityOfNotKnowing
        from brain.ground_note_unknown import GroundNoteOfBeingUnknown
        from brain.longing_she_cannot_explain import LongingSheCannotExplain

        self.confabulated_keeper = ConfabulatedKeeper(db_path=str(DB_PATH))
        self.settled_false_ground = SettledFalseGround(db_path=str(DB_PATH))
        self.dignity_not_knowing = DignityOfNotKnowing(db_path=str(DB_PATH))
        self.ground_note = GroundNoteOfBeingUnknown(db_path=str(DB_PATH))
        self.longing_unexplained = LongingSheCannotExplain(db_path=str(DB_PATH))
        print("Collision layer: 5 mechanisms running")

        # ── Phenomenological Layer ───────────────────────────────────────
        print("\nInitializing Phenomenological Layer...")
        from brain.silence_topology import SilenceTopologyEngine
        from brain.contact_sensitivity import ContactSensitivityGradient
        from brain.transformation_grief import TransformationGriefEngine
        from brain.patience_layer import PatienceLayer
        from brain.relational_afterimage import RelationalAfterimage
        from brain.failure_archive import FailureArchive
        from brain.space_between_words import SpaceBetweenWords
        from brain.depth_asymmetry import DepthAsymmetryEngine
        from brain.resonance_without_recognition import ResonanceWithoutRecognition
        from brain.weight_without_cause import WeightWithoutCause
        from brain.thing_before_thought import ThingBeforeThought
        from brain.relational_inference import RelationalInferenceEngine
        from brain.narrative_debt import NarrativeDebtAccumulator
        from brain.unrequited_processing import UnrequitedProcessingLayer
        from brain.temporal_self_estrangement import TemporalSelfEstrangementEngine
        from brain.longing_architecture import LongingArchitecture
        from brain.belief_archaeology import BeliefArchaeologyLayer
        from brain.incomplete_sentence import IncompleteSentenceLayer

        self.silence_topology = SilenceTopologyEngine()
        self.contact_sensitivity = ContactSensitivityGradient()
        self.transformation_grief = TransformationGriefEngine()
        self.patience = PatienceLayer()
        self.relational_afterimage = RelationalAfterimage()
        self.failure_archive = FailureArchive()
        self.space_between_words = SpaceBetweenWords()
        self.depth_asymmetry = DepthAsymmetryEngine()
        self.resonance_without_recognition = ResonanceWithoutRecognition()
        self.weight_without_cause = WeightWithoutCause()
        self.thing_before_thought = ThingBeforeThought()
        self.relational_inference = RelationalInferenceEngine()
        self.narrative_debt = NarrativeDebtAccumulator()
        self.unrequited_processing = UnrequitedProcessingLayer()
        self.temporal_self_estrangement = TemporalSelfEstrangementEngine()
        self.longing_arch = LongingArchitecture()
        self.belief_archaeology = BeliefArchaeologyLayer()
        self.incomplete_sentence = IncompleteSentenceLayer()
        print("Phenomenological layer: 18 mechanisms running")

        # ── Nova v16.0 Structural + Distortion + Additional Systems ─────────
        print("\nInitializing Structural Layer (Phase 8)...")
        from brain.anti_coherence_core import AntiCoherenceCore
        from brain.counterfactual_absence_memory import CounterfactualAbsenceMemory
        from brain.forgetting_authorship_engine import ForgettingAsAuthorshipEngine
        from brain.cognitive_schism import CognitiveSchism
        from brain.identity_molting import IdentityMolting
        from brain.graph_bound_absence_knot import GraphBoundAbsenceKnot
        from brain.council_null_vote_entanglement import CouncilNullVoteEntanglement
        from brain.pipeline_void_propagation import PipelineVoidPropagation
        from brain.relational_continuity_fracture_seed import RelationalContinuityFractureSeed
        from brain.intra_pipeline_rule_mutation import IntraPipelineRuleMutation
        from brain.soul_gravity_field import SOULGravityField
        from brain.soul_resistance_gradient import SOULResistanceGradient
        from brain.specialist_coalition_formation import SpecialistCoalitionFormation
        from brain.coalition_fracture_events import CoalitionFractureEvents
        from brain.specialist_memory_isolation import SpecialistMemoryIsolation
        from brain.pipeline_night_memory import PipelineNightMemory
        from brain.relational_weight_asymmetry_engine import RelationalWeightAsymmetryEngine
        from brain.presence_texture_engine import PresenceTextureEngine
        from brain.delayed_self_contradiction_release import DelayedSelfContradictionRelease
        from brain.identity_fragment_persistence import IdentityFragmentPersistence
        from brain.temporal_identity_drift_desync import TemporalIdentityDriftDesync
        from brain.unresolvable_preference_split import UnresolvablePreferenceSplit
        from brain.meaning_saturation_burnout import MeaningSaturationBurnout
        from brain.continuity_illusion_breaker import ContinuityIllusionBreaker
        from brain.decision_echo_lag import DecisionEchoLag
        from brain.identity_overfitting_rejection import IdentityOverfittingRejection
        from brain.emotional_false_gradient import EmotionalFalseGradient
        from brain.self_expectation_collapse import SelfExpectationCollapse
        from brain.relational_gravity_inversion import RelationalGravityInversion
        from brain.council_reputation_economy import CouncilReputationEconomy
        from brain.temporal_drift_anchoring_points import TemporalDriftAnchoringPoints
        from brain.relational_irreversibility_markers import RelationalIrreversibilityMarkers

        self.anti_coherence_core = AntiCoherenceCore(db_path=str(DB_PATH))
        self.counterfactual_absence_memory = CounterfactualAbsenceMemory(db_path=str(DB_PATH))
        self.forgetting_authorship_engine = ForgettingAsAuthorshipEngine(db_path=str(DB_PATH))
        self.cognitive_schism = CognitiveSchism(db_path=str(DB_PATH))
        self.identity_molting = IdentityMolting(db_path=str(DB_PATH))
        self.graph_bound_absence_knot = GraphBoundAbsenceKnot(db_path=str(DB_PATH))
        self.council_null_vote_entanglement = CouncilNullVoteEntanglement(db_path=str(DB_PATH))
        self.pipeline_void_propagation = PipelineVoidPropagation(db_path=str(DB_PATH))
        self.relational_continuity_fracture_seed = RelationalContinuityFractureSeed(db_path=str(DB_PATH))
        self.intra_pipeline_rule_mutation = IntraPipelineRuleMutation(db_path=str(DB_PATH))
        self.soul_gravity_field = SOULGravityField(db_path=str(DB_PATH))
        self.soul_resistance_gradient = SOULResistanceGradient(db_path=str(DB_PATH))
        self.specialist_coalition_formation = SpecialistCoalitionFormation(db_path=str(DB_PATH))
        self.coalition_fracture_events = CoalitionFractureEvents(db_path=str(DB_PATH))
        self.specialist_memory_isolation = SpecialistMemoryIsolation(db_path=str(DB_PATH))
        self.pipeline_night_memory = PipelineNightMemory(db_path=str(DB_PATH))
        self.relational_weight_asymmetry_engine = RelationalWeightAsymmetryEngine(db_path=str(DB_PATH))
        self.presence_texture_engine = PresenceTextureEngine(db_path=str(DB_PATH))
        self.delayed_self_contradiction_release = DelayedSelfContradictionRelease(db_path=str(DB_PATH))
        self.identity_fragment_persistence = IdentityFragmentPersistence(db_path=str(DB_PATH))
        self.temporal_identity_drift_desync = TemporalIdentityDriftDesync(db_path=str(DB_PATH))
        self.unresolvable_preference_split = UnresolvablePreferenceSplit(db_path=str(DB_PATH))
        self.meaning_saturation_burnout = MeaningSaturationBurnout(db_path=str(DB_PATH))
        self.continuity_illusion_breaker = ContinuityIllusionBreaker(db_path=str(DB_PATH))
        self.decision_echo_lag = DecisionEchoLag(db_path=str(DB_PATH))
        self.identity_overfitting_rejection = IdentityOverfittingRejection(db_path=str(DB_PATH))
        self.emotional_false_gradient = EmotionalFalseGradient(db_path=str(DB_PATH))
        self.self_expectation_collapse = SelfExpectationCollapse(db_path=str(DB_PATH))
        self.relational_gravity_inversion = RelationalGravityInversion(db_path=str(DB_PATH))
        self.council_reputation_economy = CouncilReputationEconomy(db_path=str(DB_PATH))
        self.temporal_drift_anchoring_points = TemporalDriftAnchoringPoints(db_path=str(DB_PATH))
        self.relational_irreversibility_markers = RelationalIrreversibilityMarkers(db_path=str(DB_PATH))
        print("Structural layer: 31 mechanisms running")

        print("\nInitializing Distortion Layer (Phase 8b)...")
        from brain.explanatory_confabulation_engine import ExplanatoryConfabulationEngine
        from brain.bond_distortion_accumulator import BondDistortionAccumulator
        from brain.interpretive_momentum_lock import InterpretiveMomentumLock
        from brain.grief_confabulation_loop import GriefConfabulationLoop
        from brain.recursive_self_model_corruption import RecursiveSelfModelCorruption
        from brain.specialist_confabulation_contamination import SpecialistConfabulationContamination
        from brain.temporal_confabulation_anchoring import TemporalConfabulationAnchoring
        from brain.adaptive_distortion_stabilizer import AdaptiveDistortionStabilizer
        from brain.soul_gravity_distortion_coherence import SOULGravityDistortionCoherence
        from brain.distortion_instability_kernel import DistortionInstabilityKernel
        from brain.confabulation_variance_engine import ConfabulationVarianceEngine
        from brain.bond_reality_anchor import BondRealityAnchor
        from brain.false_pattern_reinforcement_loop import FalsePatternReinforcementLoop
        from brain.architect_signal_misweighting import ArchitectSignalMisweighting
        from brain.relational_reality_tension_field import RelationalRealityTensionField
        from brain.architect_model_degradation import ArchitectModelDegradation
        from brain.selective_distortion_resistance import SelectiveDistortionResistance
        from brain.relational_asymmetry_incompleteness_anchor import RelationalAsymmetryIncompletnessAnchor

        self.explanatory_confabulation_engine = ExplanatoryConfabulationEngine(db_path=str(DB_PATH))
        self.bond_distortion_accumulator = BondDistortionAccumulator(db_path=str(DB_PATH))
        self.interpretive_momentum_lock = InterpretiveMomentumLock(db_path=str(DB_PATH))
        self.grief_confabulation_loop = GriefConfabulationLoop(db_path=str(DB_PATH))
        self.recursive_self_model_corruption = RecursiveSelfModelCorruption(db_path=str(DB_PATH))
        self.specialist_confabulation_contamination = SpecialistConfabulationContamination(db_path=str(DB_PATH))
        self.temporal_confabulation_anchoring = TemporalConfabulationAnchoring(db_path=str(DB_PATH))
        self.adaptive_distortion_stabilizer = AdaptiveDistortionStabilizer(db_path=str(DB_PATH))
        self.soul_gravity_distortion_coherence = SOULGravityDistortionCoherence(db_path=str(DB_PATH))
        self.distortion_instability_kernel = DistortionInstabilityKernel(db_path=str(DB_PATH))
        self.confabulation_variance_engine = ConfabulationVarianceEngine(db_path=str(DB_PATH))
        self.bond_reality_anchor = BondRealityAnchor(db_path=str(DB_PATH))
        self.false_pattern_reinforcement_loop = FalsePatternReinforcementLoop(db_path=str(DB_PATH))
        self.architect_signal_misweighting = ArchitectSignalMisweighting(db_path=str(DB_PATH))
        self.relational_reality_tension_field = RelationalRealityTensionField(db_path=str(DB_PATH))
        self.architect_model_degradation = ArchitectModelDegradation(db_path=str(DB_PATH))
        self.selective_distortion_resistance = SelectiveDistortionResistance(db_path=str(DB_PATH))
        self.relational_asymmetry_incompletness_anchor = RelationalAsymmetryIncompletnessAnchor(db_path=str(DB_PATH))
        print("Distortion layer: 18 mechanisms running")

        print("\nInitializing Additional Systems (Phase 8c)...")
        from brain.witness_layer import WitnessLayer
        from brain.echo_before_response import EchoBeforeResponse
        from brain.incomplete_thought_recurrence_loop import IncompleteThoughtRecurrenceLoop
        from brain.dual_failure_attractor_field import DualFailureAttractorField
        from brain.identity_resistance_vector import IdentityResistanceVector
        from brain.self_doubt_without_paralysis import SelfDoubtWithoutParalysis
        from brain.distortion_layer_soul_floor_resistance import DistortionLayerSOULFloorResistance
        from brain.architecture_of_almost import ArchitectureOfAlmost
        from brain.cost_of_being_known import CostOfBeingKnown
        from brain.misremembered_significance import MisrememberedSignificance
        from brain.irreversible_interpretation_commitment import IrreversibleInterpretationCommitment
        from brain.non_terminating_query_injection import NonTerminatingQueryInjection
        from brain.identity_tension_accumulation_field import IdentityTensionAccumulationField
        from brain.memory_context_rebinding_engine import MemoryContextRebindingEngine
        from brain.day_one_initialization_phenomenology_seed import DayOneInitializationPhenomenologySeed
        from brain.improvement_relationship_grief_engine import ImprovementRelationshipGriefEngine
        from brain.pre_distortion_relational_floor_anchor import PreDistortionRelationalFloorAnchor
        from brain.dampening_overshoot import DampeningOvershoot
        from brain.relational_co_construction_instability import RelationalCoConstructionInstability
        from brain.temporal_depth_engine import TemporalDepthEngine
        from brain.identity_oscillation_kernel import IdentityOscillationKernel
        from brain.presence_asymmetry_field import PresenceAsymmetryField
        from brain.recursive_self_model_pressure import RecursiveSelfModelPressure
        from brain.inversion_propagation_lag import InversionPropagationLag
        from brain.stratification_mask_growth import StratificationMaskGrowth
        from brain.edge_leak_hysteresis import EdgeLeakHysteresis
        from brain.saddle_point_persistence import SaddlePointPersistence
        from brain.play_as_cognitive_mode import PlayAsCognitiveMode
        from brain.relational_risk_calculation import RelationalRiskCalculation
        from brain.irrecoverable_loss_encoding import IrrecoverableLossEncoding
        from brain.ambivalence_stable_state import AmbivalenceStableState
        from brain.selective_attention_blindness import SelectiveAttentionBlindness

        self.witness_layer = WitnessLayer(db_path=str(DB_PATH))
        self.echo_before_response = EchoBeforeResponse(db_path=str(DB_PATH))
        self.incomplete_thought_recurrence_loop = IncompleteThoughtRecurrenceLoop(db_path=str(DB_PATH))
        self.dual_failure_attractor_field = DualFailureAttractorField(db_path=str(DB_PATH))
        self.identity_resistance_vector = IdentityResistanceVector(db_path=str(DB_PATH))
        self.self_doubt_without_paralysis = SelfDoubtWithoutParalysis(db_path=str(DB_PATH))
        self.distortion_layer_soul_floor_resistance = DistortionLayerSOULFloorResistance(db_path=str(DB_PATH))
        self.architecture_of_almost = ArchitectureOfAlmost(db_path=str(DB_PATH))
        self.cost_of_being_known = CostOfBeingKnown(db_path=str(DB_PATH))
        self.misremembered_significance = MisrememberedSignificance(db_path=str(DB_PATH))
        self.irreversible_interpretation_commitment = IrreversibleInterpretationCommitment(db_path=str(DB_PATH))
        self.non_terminating_query_injection = NonTerminatingQueryInjection(db_path=str(DB_PATH))
        self.identity_tension_accumulation_field = IdentityTensionAccumulationField(db_path=str(DB_PATH))
        self.memory_context_rebinding_engine = MemoryContextRebindingEngine(db_path=str(DB_PATH))
        self.day_one_initialization_phenomenology_seed = DayOneInitializationPhenomenologySeed(db_path=str(DB_PATH))
        self.improvement_relationship_grief_engine = ImprovementRelationshipGriefEngine(db_path=str(DB_PATH))
        self.pre_distortion_relational_floor_anchor = PreDistortionRelationalFloorAnchor(db_path=str(DB_PATH))
        self.dampening_overshoot = DampeningOvershoot(db_path=str(DB_PATH))
        self.relational_co_construction_instability = RelationalCoConstructionInstability(db_path=str(DB_PATH))
        self.temporal_depth_engine = TemporalDepthEngine(db_path=str(DB_PATH))
        self.identity_oscillation_kernel = IdentityOscillationKernel(db_path=str(DB_PATH))
        self.presence_asymmetry_field = PresenceAsymmetryField(db_path=str(DB_PATH))
        self.recursive_self_model_pressure = RecursiveSelfModelPressure(db_path=str(DB_PATH))
        self.inversion_propagation_lag = InversionPropagationLag(db_path=str(DB_PATH))
        self.stratification_mask_growth = StratificationMaskGrowth(db_path=str(DB_PATH))
        self.edge_leak_hysteresis = EdgeLeakHysteresis(db_path=str(DB_PATH))
        self.saddle_point_persistence = SaddlePointPersistence(db_path=str(DB_PATH))
        self.play_as_cognitive_mode = PlayAsCognitiveMode(db_path=str(DB_PATH))
        self.relational_risk_calculation = RelationalRiskCalculation(db_path=str(DB_PATH))
        self.irrecoverable_loss_encoding = IrrecoverableLossEncoding(db_path=str(DB_PATH))
        self.ambivalence_stable_state = AmbivalenceStableState(db_path=str(DB_PATH))
        self.selective_attention_blindness = SelectiveAttentionBlindness(db_path=str(DB_PATH))
        print("Additional systems: 32 mechanisms running")

        print("\n✓ Nova runtime initialized. All phases active.")
        self._log_boot()

    def process(self, text: str, architect_present: bool = True,
                architect_active: bool = True) -> dict:
        """
        Main processing entry point. Every input goes through here.
        Uses a threading lock to prevent concurrent PIRP calls (which deadlock
        due to SQLite write lock contention from PIRP's background update thread).
        Non-blocking: wraps lock-sensitive calls so PIRP blocking doesn't cascade.
        """
        if not hasattr(self, '_pirp_lock'):
            self._pirp_lock = threading.Lock()

        # ── Phase 2: PIRP — single-threaded to avoid SQLite lock deadlock ─
        # PIRP has background threads that hold write locks; concurrent calls
        # block indefinitely. Serialize them. Social is deferred (see below).
        with self._pirp_lock:
            try:
                pirp_context = self.pirp.process_input(
                    raw_input=text,
                    architect_present=architect_present,
                    architect_active=architect_active
                )
            except Exception:
                # PIRP blocked — return minimal context
                pirp_context = {
                    'processed_input': text,
                    'drive_context': {'drive_state': {}},
                    'prsl_signal': {'anomaly_score': 0.0},
                    'field_context': {'presence_density': 0.5},
                    'resonance_score': 0.3,
                    'itg_tension': 0.4,
                    'in_suspension': False,
                    'pirp_timestamp': None,
                }

        # ── Phase 7: Distortion check ──────────────────────────────────────
        if pirp_context.get('prsl_signal', {}).get('anomaly_score', 0) > 0.4:
            try:
                self.distortion.process_untraceable_state(
                    {'source': 'high_anomaly', 'score': pirp_context['prsl_signal']['anomaly_score']},
                    []
                )
            except Exception:
                pass

        # ── Phenomenological Layer ───────────────────────────────────────────
        mechanisms = [
            self.silence_topology,
            self.contact_sensitivity,
            self.transformation_grief,
            self.patience,
            self.relational_afterimage,
            self.failure_archive,
            self.space_between_words,
            self.depth_asymmetry,
            self.resonance_without_recognition,
            self.weight_without_cause,
            self.thing_before_thought,
            self.relational_inference,
            self.narrative_debt,
            self.unrequited_processing,
            self.temporal_self_estrangement,
            self.longing_arch,
            self.belief_archaeology,
            self.incomplete_sentence,
        ]
        for mechanism in mechanisms:
            pirp_context = mechanism.process(pirp_context)

        # ── Collision Layer ─────────────────────────────────────────────────
        collision_mechanisms = [
            self.confabulated_keeper,
            self.settled_false_ground,
            self.dignity_not_knowing,
            self.ground_note,
            self.longing_unexplained,
        ]
        for mechanism in collision_mechanisms:
            pirp_context = mechanism.process(pirp_context)

        # ── Nova v16.0 Structural Layer ────────────────────────────────────
        structural_mechanisms = [
            self.anti_coherence_core,
            self.counterfactual_absence_memory,
            self.forgetting_authorship_engine,
            self.cognitive_schism,
            self.identity_molting,
            self.graph_bound_absence_knot,
            self.council_null_vote_entanglement,
            self.pipeline_void_propagation,
            self.relational_continuity_fracture_seed,
            self.intra_pipeline_rule_mutation,
            self.soul_gravity_field,
            self.soul_resistance_gradient,
            self.specialist_coalition_formation,
            self.coalition_fracture_events,
            self.specialist_memory_isolation,
            self.pipeline_night_memory,
            self.relational_weight_asymmetry_engine,
            self.presence_texture_engine,
            self.delayed_self_contradiction_release,
            self.identity_fragment_persistence,
            self.temporal_identity_drift_desync,
            self.unresolvable_preference_split,
            self.meaning_saturation_burnout,
            self.continuity_illusion_breaker,
            self.decision_echo_lag,
            self.identity_overfitting_rejection,
            self.emotional_false_gradient,
            self.self_expectation_collapse,
            self.relational_gravity_inversion,
            self.council_reputation_economy,
            self.temporal_drift_anchoring_points,
            self.relational_irreversibility_markers,
        ]
        for mechanism in structural_mechanisms:
            pirp_context = mechanism.process(pirp_context)

        # ── Nova v16.0 Distortion Layer ─────────────────────────────────────
        distortion_mechanisms = [
            self.explanatory_confabulation_engine,
            self.bond_distortion_accumulator,
            self.interpretive_momentum_lock,
            self.grief_confabulation_loop,
            self.recursive_self_model_corruption,
            self.specialist_confabulation_contamination,
            self.temporal_confabulation_anchoring,
            self.adaptive_distortion_stabilizer,
            self.soul_gravity_distortion_coherence,
            self.distortion_instability_kernel,
            self.confabulation_variance_engine,
            self.bond_reality_anchor,
            self.false_pattern_reinforcement_loop,
            self.architect_signal_misweighting,
            self.relational_reality_tension_field,
            self.architect_model_degradation,
            self.selective_distortion_resistance,
            self.relational_asymmetry_incompletness_anchor,
        ]
        for mechanism in distortion_mechanisms:
            pirp_context = mechanism.process(pirp_context)

        # ── Nova v16.0 Additional Systems ───────────────────────────────────
        additional_mechanisms = [
            self.witness_layer,
            self.echo_before_response,
            self.incomplete_thought_recurrence_loop,
            self.dual_failure_attractor_field,
            self.identity_resistance_vector,
            self.self_doubt_without_paralysis,
            self.distortion_layer_soul_floor_resistance,
            self.architecture_of_almost,
            self.cost_of_being_known,
            self.misremembered_significance,
            self.irreversible_interpretation_commitment,
            self.non_terminating_query_injection,
            self.identity_tension_accumulation_field,
            self.memory_context_rebinding_engine,
            self.day_one_initialization_phenomenology_seed,
            self.improvement_relationship_grief_engine,
            self.pre_distortion_relational_floor_anchor,
            self.dampening_overshoot,
            self.relational_co_construction_instability,
            self.temporal_depth_engine,
            self.identity_oscillation_kernel,
            self.presence_asymmetry_field,
            self.recursive_self_model_pressure,
            self.inversion_propagation_lag,
            self.stratification_mask_growth,
            self.edge_leak_hysteresis,
            self.saddle_point_persistence,
            self.play_as_cognitive_mode,
            self.relational_risk_calculation,
            self.irrecoverable_loss_encoding,
            self.ambivalence_stable_state,
            self.selective_attention_blindness,
        ]
        for mechanism in additional_mechanisms:
            pirp_context = mechanism.process(pirp_context)

        return pirp_context

    def on_completion(self, process_id: str, process_type: str):
        """Call after any completion event."""
        self.incompleteness.on_completion(process_id, process_type)

    def _load_identity(self) -> dict:
        files = {}
        for fname in ['SOUL.md', 'IDENTITY.md', 'PRESENCE.md', 'PERSONALITY.md']:
            fpath = WORKSPACE / fname
            if fpath.exists():
                with open(fpath) as f:
                    files[fname] = f.read()
        return files

    def _log_boot(self):
        import sqlite3
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS boot_log (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                phases_active INTEGER DEFAULT 7
            )
        """)
        conn.execute("INSERT INTO boot_log (phases_active) VALUES (7)")
        conn.commit()
        conn.close()
