"""Evidence migration parity test (RDE-034).

Every file mapped from a stage-coded directory into a neutral
publication directory was copied byte-for-byte. This test pins the
SHA256 of each migrated file so any later corruption or silent edit
fails loudly. Old stage-coded directories must be gone.
"""

import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EV = REPO / "paper" / "evidence"

# SHA256 recorded at migration time (byte-identical copies).
EXPECTED = {
    "endpoints/domain_split.json": "347e6f6ef97b92b27d1adf9877fdd6aa19269f9dc5e6d44af030c49e0caa67db",
    "endpoints/difference_fields.npz": "bc635ee5b12a20c3bb9355b1ca40632e456e1227dbff33f3d47a85d46405eb5b",
    "endpoints/calibration_contract.json": "e3af09f021e401366492e1f1e2b161dde91fd54e3ec2b385b04bbed62511f4ca",
    "endpoints/endpoint_cmb_1.json": "154266db718f6c0aea808bab2e3340d3fe1e1d8bf271f5283f4cae2fb43b01dd",
    "endpoints/endpoint_cmb_2.json": "43fd840abb45712bbbbffbf0721043dea1e19d9c32f167cfcd2fa82bc7d315c9",
    "endpoints/endpoint_identity.json": "1ae0864f00b14f085a839f4b6461a809271fffb7c2480e520026642473cd300f",
    "endpoints/endpoint_manifest.json": "4902356dab89f84acbe725c5e279d363359d95f175f23d7646ba981843e5b268",
    "endpoints/endpoint_redshift.json": "fb44b238a6e69c750066dee38df9ace85a2397472450d68929c0b26a8f919fb5",
    "likelihood/claim_contract.json": "df652d73434a1d33f7aa23852ca0389aa428d93624d1366c2f5c56095cf694d5",
    "likelihood/desi_null_cv.csv": "d286bfac13cea182f9a86187e94ec5ce6b969d56193ea19cbd5a3ffab15d117b",
    "likelihood/null_model_contract.json": "099b6b7b2d4bef5547b52e729a7fe2973b454360b9bacc18b8e6cd7c317f9d18",
    "likelihood/sn_null_cv.csv": "c100cacd2ffcac81e87f9aa0c69b624af7c4b37c06e7fd33f06bb3c76bd4b968",
    "likelihood/sn_selection_contract.json": "0a55fae7a4fb8878c7db12bb5db021e0d92c8e6a3775c2c0b7c95b9c640fc2f1",
    "model_selection/bootstrap.json": "1fc7784f902570a8a4859bbffee3de654058efde2868efd05911ee2109b04d45",
    "model_selection/constrained_cv.json": "5a276eef8789bbc405d169e3b85ce8d551bc402cb349d0525bad1347ffdc71bb",
    "reconstruction/control_endpoint.json": "a94100ef5896b9eaae58c50e5f1dcd1125e96115529c7f813dabf275df5022ed",
    "reconstruction/desi_cv_by_order.csv": "d5509b8509c4dab849b2362be32e688a0b670dc6404ed55a3f76673f8320dd5c",
    "reconstruction/epsilon_profile.json": "a7999fb58b9cdeea51c7b1fc422620f3191b44af4eaa93f81a066a657acec63b",
    "reconstruction/external_prediction_contract.json": "30d994453bd3b1b944a2122f2308ca64ee5ce22db6895fadbd411b2cf780af18",
    "reconstruction/information_criteria.json": "0edcf9dd1aa67eb8af97e21d3c783eab39a6ebbe8182c919f45eef5c65992a47",
    "reconstruction/information_criteria.txt": "8ac091c638973a3861a3ec3425ed828b0eccf2206f11ab648a3901a9161bae3a",
    "reconstruction/jacobian_rank.json": "56cb7013c2d4ad10822ecde2bf5d47c320e4a3897f294b336f3a908d53382ea6",
    "reconstruction/lya_leverage.json": "c43c5991f823f7a2a0118b78f401ed79d4c753b536ea58f73527dce370769805",
    "reconstruction/null_cv_summary.json": "44c89ac53408b8b67b121fcb4c8960029409426ff4f2b74a727d597a6df8197d",
    "reconstruction/observable_mode_profiles.json": "c19731563a541cdb5946f116fc1142997177698b1768178ea07412712d749e3a",
    "reconstruction/rank_operator_contract.json": "8f3b5bc0312e0f7206b1cc2b35742b53eb587dcd6da7f6e1b30c5ef4b670e7a9",
    "reconstruction/redshift_localization.json": "54a7ff76a944d85b777bc9f2d8a5438dbed6357dbb207dea7b899a91c54b45af",
    "reconstruction/roughness_bound_audit.json": "41ee4f9bfc6b046ec26f5c5d8c924649c02f8a81333b1f4f1bbcf334047c9319",
    "reconstruction/selection_bootstrap.json": "bb9e42d290288d50d25a4ac4ffadbaa7cc18b286fa4e54f441a74e77c4096bb4",
    "reconstruction/selection_bootstrap_pilot.json": "ca3ade412c296a6a8e516e24a98a019656f41a723caef4b5118d005d6eab12dc",
    "reconstruction/shape_comparison.json": "d24a3c180d79c1f83e3bfa6ff4ca996e92ac264c2f102b87f17c753f92802005",
    "reconstruction/sn_cv_by_order.csv": "999da8ec227612c7e318b004ad9597b0ab1113619952176c65d58a4b55af684c",
    "reconstruction/summary.json": "9c8d9d54c234ee97253a33ec066873cc9e6a603cd4a2ae588f8c22249cb016e0",
    "reconstruction/visible_map.json": "700e2df24f5c533d22c0fb101a55237bda5bbb991fdf67c86b75b6acd3f156a7",
    "reference_sensitivity/agreement_metrics.json": "b524cd2b2e37d2d6c513b135eb09a6d9c5219ac54a2d0a35acc0a349a3472905",
    "reference_sensitivity/common_mode.json": "409aa6416a93676cf170238696208ace086d9fda2db5583703674496776f8740",
    "reference_sensitivity/difference_fields.npz": "bc635ee5b12a20c3bb9355b1ca40632e456e1227dbff33f3d47a85d46405eb5b",
    "reference_sensitivity/disposition.json": "c0ffb7b06ec8d1a82412b3879d60f5f80322547dce29888efd9fa1401593ef00",
    "reference_sensitivity/domain_split.json": "347e6f6ef97b92b27d1adf9877fdd6aa19269f9dc5e6d44af030c49e0caa67db",
    "reference_sensitivity/overlay_curves.json": "45c4489efcd2c6bfc46591ab374c5f0d53202bc4638a292e6793ae17e498908d",
    "reference_sensitivity/overlay_curves.npz": "26097f740e32b94f2033bb9703577cc366e6bdfc9c05aeb30fad71790043a5c6",
    "reference_sensitivity/scale_comparison.json": "57fb19c3a9306496c5a1ee4206644713698a73e170393cf447e84bcf7833af64",
    "reference_sensitivity/transfer_results.json": "86bb341c87fd881ade1202955a1a70f289e5d7bda66d1f632a2dad5266866fe8",
    "reference_sensitivity/vs_prior.json": "6f89228c343e51d7f38d36486b0eee916f438c11d7e629c2337c2a6ad872035e",
}
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def test_stage_coded_directories_removed():
    for old in ("cmb_bridge_" + "r" + "4v", "cmb_bridge_" + "r" + "5", "cmb_bridge_" + "r" + "6", "cmb_bridge_" + "r" + "8r2"):
        assert not (EV / old).exists(), f"stage-coded directory remains: {old}"


def test_migrated_bytes_unchanged():
    failures = []
    for rel, expected in EXPECTED.items():
        path = EV / rel
        if not path.exists():
            failures.append(f"missing: {rel}")
        elif sha256_of(path) != expected:
            failures.append(f"hash changed: {rel}")
    assert not failures, "\n".join(failures)
