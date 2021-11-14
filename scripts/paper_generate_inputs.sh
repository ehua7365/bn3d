paper_dir=temp/paper
mkdir -p "$paper_dir"
sbatch_dir=temp/paper/sbatch
mkdir -p "$sbatch_dir"

ratio=equal
wall_time="0-00:59"
queue=debugq

# Regime where finite-size scaling starts to break down
: '
name=rot_bposd_xzzx_zbias
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation xzzx --ratio "$ratio" \
    --sizes "2,4,6,8,10" --decoder BeliefPropagationOSDDecoder  --bias Z \
    --eta "60,70,80" --prob "0.30:0.40:0.01"
bn3d pi-sbatch --data_dir "$paper_dir/$name" --n_array 10 --queue $queue \
    --wall_time "$wall_time" --trials 10000 --split 10 $sbatch_dir/$name.sbatch
'

# Subthreshold scaling.
: '

name=sts_rot_bposd_undef_zbias
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation none --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder BeliefPropagationOSDDecoder  --bias Z \
    --eta "1" --prob "0.06"
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation none --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder BeliefPropagationOSDDecoder  --bias Z \
    --eta "1,10,100,1000,inf" --prob "0.08"
bn3d pi-sbatch --data_dir "$paper_dir/$name" --n_array 6 --queue $queue \
    --wall_time "$wall_time" --trials 100000 --split 80 $sbatch_dir/$name.sbatch

name=sts_rot_bposd_xzzx_zbias
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation xzzx --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder BeliefPropagationOSDDecoder  --bias Z \
    --eta "1" --prob "0.05"
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation xzzx --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder BeliefPropagationOSDDecoder  --bias Z \
    --eta "10" --prob "0.10"
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation xzzx --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder BeliefPropagationOSDDecoder  --bias Z \
    --eta "100,1000,inf" --prob "0.25"
bn3d pi-sbatch --data_dir "$paper_dir/$name" --n_array 6 --queue $queue \
    --wall_time "$wall_time" --trials 100000 --split 80 $sbatch_dir/$name.sbatch

name=sts_rot_sweepmatch_undef_zbias
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation none --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder RotatedSweepMatchDecoder  --bias Z \
    --eta "1,10,100,1000,inf" --prob "0.08"
bn3d pi-sbatch --data_dir "$paper_dir/$name" --n_array 6 --queue $queue \
    --wall_time "$wall_time" --trials 100000 --split 60 $sbatch_dir/$name.sbatch

name=sts_rot_sweepmatch_xy_zbias
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation xy --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder RotatedSweepMatchDecoder  --bias Z \
    --eta "1,10,100,1000,inf" --prob "0.08"
bn3d pi-sbatch --data_dir "$paper_dir/$name" --n_array 6 --queue $queue \
    --wall_time "$wall_time" --trials 100000 --split 60 $sbatch_dir/$name.sbatch
'


# Main runs Z bias
: '
name=rot_bposd_undef_zbias 
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation none --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder BeliefPropagationOSDDecoder   --bias Z \
    --eta "0.5,1,3" --prob "0:0.18:0.01"
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation none --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder BeliefPropagationOSDDecoder   --bias Z \
    --eta "10,30,100,inf" --prob "0.18:0.27:0.01"
bn3d pi-sbatch --data_dir "$paper_dir/$name" --n_array 6 --queue $queue \
    --wall_time "$wall_time" --trials 10000 --split 10 $sbatch_dir/$name.sbatch

name=rot_bposd_xzzx_zbias  
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation xzzx --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder BeliefPropagationOSDDecoder   --bias Z \
    --eta "0.5,1,3" --prob "0:0.18:0.01"
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation xzzx --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder BeliefPropagationOSDDecoder   --bias Z \
    --eta "10,30,100,inf" --prob "0.18:0.55:0.01"
bn3d pi-sbatch --data_dir "$paper_dir/$name" --n_array 6 --queue $queue \
    --wall_time "$wall_time" --trials 10000 --split 10 $sbatch_dir/$name.sbatch

name=rot_sweepmatch_undef_zbias   
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation none --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder RotatedSweepMatchDecoder    --bias Z \
    --eta "0.5,1,3,10,30,100,inf" --prob "0:0.55:0.01"
bn3d pi-sbatch --data_dir "$paper_dir/$name" --n_array 6 --queue $queue \
    --wall_time "$wall_time" --trials 10000 --split 10 $sbatch_dir/$name.sbatch
'

name=rot_sweepmatch_undef_zbias
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation none --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder RotatedSweepMatchDecoder --bias Z \
    --eta "0.5,inf" --prob "0:0.5:0.01"
bn3d pi-sbatch --data_dir "$paper_dir/$name" --n_array 6 --queue $queue \
    --wall_time "$wall_time" --trials 1000 --split 10 $sbatch_dir/$name.sbatch

name=rot_sweepmatch_xzzx_zbias
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation xzzx --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder RotatedSweepMatchDecoder --bias Z \
    --eta "0.5,inf" --prob "0:0.5:0.01"
bn3d pi-sbatch --data_dir "$paper_dir/$name" --n_array 6 --queue $queue \
    --wall_time "$wall_time" --trials 1000 --split 10 $sbatch_dir/$name.sbatch

name=unrot_sweepmatch_undef_zbias
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice kitaev --boundary toric --deformation none  --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder SweepMatchDecoder --bias Z \
    --eta "0.5,inf" --prob "0:0.5:0.01"
bn3d pi-sbatch --data_dir "$paper_dir/$name" --n_array 6 --queue $queue \
    --wall_time "$wall_time" --trials 1000 --split 10 $sbatch_dir/$name.sbatch

name=unrot_sweepmatch_xzzx_zbias
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice kitaev --boundary toric --deformation xzzx --ratio "$ratio" \
    --sizes "2,4,6,8" --decoder SweepMatchDecoder --bias Z \
    --eta "0.5,inf" --prob "0:0.5:0.01"
bn3d pi-sbatch --data_dir "$paper_dir/$name" --n_array 6 --queue $queue \
    --wall_time "$wall_time" --trials 1000 --split 10 $sbatch_dir/$name.sbatch

: '
# Detailed run infinite Z bias
name=det_rot_bposd_xzzx_zbias  
bn3d generate-input -i "$paper_dir/$name/inputs" \
    --lattice rotated --boundary planar --deformation xzzx --ratio "$ratio" \
    --sizes "2,4,6,8,10" --decoder BeliefPropagationOSDDecoder --bias Z \
    --eta "inf" --prob "0.32:0.38:0.005"
bn3d pi-sbatch --data_dir "$paper_dir/$name" --n_array 12 --queue $queue \
    --wall_time "$wall_time" --trials 100000 --split 25 $sbatch_dir/$name.sbatch
'

: '
setup_dir rot_bposd_undef_xbias rotated BeliefPropagationOSDDecoder none X \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
setup_dir rot_bposd_undef_zbias rotated BeliefPropagationOSDDecoder none Z \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
setup_dir rot_bposd_xzzx_xbias rotated BeliefPropagationOSDDecoder xzzx X \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
setup_dir rot_bposd_xzzx_zbias rotated BeliefPropagationOSDDecoder xzzx Z \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
setup_dir rot_sweepmatch_undef_xbias rotated RotatedSweepMatchDecoder none X \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
setup_dir rot_sweepmatch_undef_zbias rotated RotatedSweepMatchDecoder none Z \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
setup_dir rot_sweepmatch_xy_xbias rotated RotatedSweepMatchDecoder xy X \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
setup_dir rot_sweepmatch_xy_zbias rotated RotatedSweepMatchDecoder xy Z \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"

setup_dir unrot_bposd_undef_xbias kitaev BeliefPropagationOSDDecoder none X \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
setup_dir unrot_bposd_undef_zbias kitaev BeliefPropagationOSDDecoder none Z \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
setup_dir unrot_bposd_xzzx_xbias kitaev BeliefPropagationOSDDecoder xzzx X \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
setup_dir unrot_bposd_xzzx_zbias kitaev BeliefPropagationOSDDecoder xzzx Z \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
setup_dir unrot_sweepmatch_undef_xbias kitaev SweepMatchDecoder none X \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
setup_dir unrot_sweepmatch_undef_zbias kitaev SweepMatchDecoder none Z \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
setup_dir unrot_sweepmatch_xy_xbias kitaev SweepMatchDecoder xy X \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
setup_dir unrot_sweepmatch_xy_zbias kitaev SweepMatchDecoder xy Z \
        "0.5,1,3,10,30,100,inf" "0:0.55:0.01"
'
