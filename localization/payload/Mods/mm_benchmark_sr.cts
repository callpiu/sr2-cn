// -------
#Groups
// -------

$Group:	"mm_benchmark_sr_$npc_group"
$Group:	"mm_benchmark_sr_$vehicle_group"
// -------
#Navpoints
// -------

$Navpoint:	"mm_benchmark_sr_$camera"
$Type:		"floating"
$Pos:			<-290 -2 -128>
$Orient:		[<0.933582 0 -0.358362> <0.024998 0.997564 0.065122> <0.357490 -0.069755 0.931308>]

$Navpoint:	"mm_benchmark_sr_$vehicle_nav_0"
$Type:		"ground"
$Pos:			<-289.618500 -6.029486 -108.019394>
$Orient:		[2.725431]

$Navpoint:	"mm_benchmark_sr_$vehicle_nav_1"
$Type:		"ground"
$Pos:			<-275.723358 -4.179000 -115.292885>
$Orient:		[-0.191729]

$Navpoint:	"mm_benchmark_sr_$vehicle_nav_2"
$Type:		"ground"
$Pos:			<-274.264557 -4.179000 -108.258331>
$Orient:		[-3.125797]

$Navpoint:	"mm_benchmark_sr_$vehicle_nav_3"
$Type:		"ground"
$Pos:			<-278.686676 -4.178952 -92.602371>
$Orient:		[-1.579590]

$Navpoint:	"mm_benchmark_sr_$vehicle_nav_4"
$Type:		"ground"
$Pos:			<-257.192993 -4.121824 -71.364815>
$Orient:		[2.304980]

$Navpoint:	"mm_benchmark_sr_$vehicle_nav_5"
$Type:		"ground"
$Pos:			<-295.751709 0.233998 -96.353287>
$Orient:		[-3.014138]

$Navpoint:	"mm_benchmark_sr_$human_nav_0"
$Type:		"ground"
$Pos:			<-283.327911 -9.078844 -111.207535>
$Orient:		[-2.021410]

$Navpoint:	"mm_benchmark_sr_$human_nav_1"
$Type:		"ground"
$Pos:			<-275.252716 -4.179000 -112.827278>
$Orient:		[-2.077339]

$Navpoint:	"mm_benchmark_sr_$human_nav_2"
$Type:		"ground"
$Pos:			<-289.340332 -5.304000 -122.143959>
$Orient:		[3.107691]

$Navpoint:	"mm_benchmark_sr_$human_nav_3"
$Type:		"ground"
$Pos:			<-285.985626 -5.304000 -123.218422>
$Orient:		[-2.071175]

$Navpoint:	"mm_benchmark_sr_$human_nav_4"
$Type:		"ground"
$Pos:			<-296.662415 0.233998 -100.922440>
$Orient:		[2.607237]

$Navpoint:	"mm_benchmark_sr_$human_nav_5"
$Type:		"ground"
$Pos:			<-274.123444 -4.178548 -94.009140>
$Orient:		[-2.622691]

$Navpoint:	"mm_benchmark_sr_$human_nav_6"
$Type:		"ground"
$Pos:			<-253.437622 -3.999002 -43.809895>
$Orient:		[0.007122]

$Navpoint:	"mm_benchmark_sr_$human_nav_7"
$Type:		"ground"
$Pos:			<-251.767242 -3.999001 -43.346062>
$Orient:		[0.000008]

$Navpoint:	"mm_benchmark_sr_$human_nav_8"
$Type:		"ground"
$Pos:			<-250.387360 -3.998993 -44.000244>
$Orient:		[0.000027]

$Navpoint:	"mm_benchmark_sr_$human_nav_9"
$Type:		"ground"
$Pos:			<-248.708893 -3.999000 -43.480709>
$Orient:		[0.000222]

$Navpoint:	"mm_benchmark_sr_$human_nav_10"
$Type:		"ground"
$Pos:			<-247.286316 -3.999000 -43.910084>
$Orient:		[0.000222]

$Navpoint:	"mm_benchmark_sr_$human_nav_11"
$Type:		"ground"
$Pos:			<-246.095322 -3.999002 -43.535118>
$Orient:		[0.000222]

$Navpoint:	"mm_benchmark_sr_$human_nav_12"
$Type:		"ground"
$Pos:			<-268.386719 -4.178415 -90.110825>
$Orient:		[0.007122]

$Navpoint:	"mm_benchmark_sr_$human_nav_13"
$Type:		"ground"
$Pos:			<-260.596588 -4.178421 -99.514496>
$Orient:		[1.005573]

$Navpoint:	"mm_benchmark_sr_$human_nav_14"
$Type:		"ground"
$Pos:			<-263.894501 -4.002000 -71.506645>
$Orient:		[-0.739149]

$Navpoint:	"mm_benchmark_sr_$human_nav_15"
$Type:		"ground"
$Pos:			<-256.361877 -4.178154 -98.548805>
$Orient:		[-0.976764]

$Navpoint:	"mm_benchmark_sr_$human_nav_16"
$Type:		"ground"
$Pos:			<-265.456635 -4.002000 -71.020660>
$Orient:		[2.176780]

$Navpoint:	"mm_benchmark_sr_$human_nav_17"
$Type:		"ground"
$Pos:			<-280.183350 -4.322937 -87.705589>
$Orient:		[2.433175]

// -------
#Paths
// -------

// -------
#Items
// -------

// -------
#Triggers
// -------

// -------
#Vehicles
// -------

$Vehicle:		"mm_benchmark_sr_$vehicle_0"
$Vehicle type:	"boat_speed01"
$Start nav:		"mm_benchmark_sr_$vehicle_nav_0"
$Group:			"mm_benchmark_sr_$vehicle_group"
$Stream Distance:			50.000
+Variant: "Police"

$Vehicle:		"mm_benchmark_sr_$vehicle_1"
$Vehicle type:	"bike_rocket02"
$Start nav:		"mm_benchmark_sr_$vehicle_nav_1"
$Group:			"mm_benchmark_sr_$vehicle_group"
$Stream Distance:			50.000
+Variant: "Gang_Ronin"

$Vehicle:		"mm_benchmark_sr_$vehicle_2"
$Vehicle type:	"car_2dr_exoticsports05"
$Start nav:		"mm_benchmark_sr_$vehicle_nav_2"
$Group:			"mm_benchmark_sr_$vehicle_group"
$Stream Distance:			50.000
+Variant: "Bling"

$Vehicle:		"mm_benchmark_sr_$vehicle_3"
$Vehicle type:	"car_2dr_compact04"
$Start nav:		"mm_benchmark_sr_$vehicle_nav_3"
$Group:			"mm_benchmark_sr_$vehicle_group"
$Stream Distance:			50.000
+Variant: "Beater"

$Vehicle:		"mm_benchmark_sr_$vehicle_4"
$Vehicle type:	"truck_2dr_pickup03"
$Start nav:		"mm_benchmark_sr_$vehicle_nav_4"
$Group:			"mm_benchmark_sr_$vehicle_group"
$Stream Distance:			50.000
+Variant: "Standard"

$Vehicle:		"mm_benchmark_sr_$vehicle_5"
$Vehicle type:	"suv_4dr_luxury01"
$Start nav:		"mm_benchmark_sr_$vehicle_nav_5"
$Group:			"mm_benchmark_sr_$vehicle_group"
$Stream Distance:			50.000
+Variant: "Bling"

// -------
#Respawns
// -------

// -------
#Humans
// -------

$Human:					"mm_benchmark_sr_$human_0"
$Char type:				"npc_Shaundi"
$Start nav:				"mm_benchmark_sr_$human_nav_0"
+Group:					"mm_benchmark_sr_$npc_group"

$Human:					"mm_benchmark_sr_$human_1"
$Char type:				"npc_cop"
$Start nav:				"mm_benchmark_sr_$human_nav_1"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"beat white male"

$Human:					"mm_benchmark_sr_$human_2"
$Char type:				"npc_tribal_male_soldier"
$Start nav:				"mm_benchmark_sr_$human_nav_2"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"hispanic"

$Human:					"mm_benchmark_sr_$human_3"
$Char type:				"npc_young_female_generic"
$Start nav:				"mm_benchmark_sr_$human_nav_3"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"student white"

$Human:					"mm_benchmark_sr_$human_4"
$Char type:				"npc_tribal_male_soldier"
$Start nav:				"mm_benchmark_sr_$human_nav_4"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"white"

$Human:					"mm_benchmark_sr_$human_5"
$Char type:				"npc_cop"
$Start nav:				"mm_benchmark_sr_$human_nav_5"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"beat asian female"

$Human:					"mm_benchmark_sr_$human_6"
$Char type:				"npc_young_female_generic"
$Start nav:				"mm_benchmark_sr_$human_nav_6"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"generic white"

$Human:					"mm_benchmark_sr_$human_7"
$Char type:				"npc_young_female_generic"
$Start nav:				"mm_benchmark_sr_$human_nav_7"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"generic black"

$Human:					"mm_benchmark_sr_$human_8"
$Char type:				"npc_tribal_male_soldier"
$Start nav:				"mm_benchmark_sr_$human_nav_8"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"white"

$Human:					"mm_benchmark_sr_$human_9"
$Char type:				"npc_young_female_generic"
$Start nav:				"mm_benchmark_sr_$human_nav_9"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"generic asian"

$Human:					"mm_benchmark_sr_$human_10"
$Char type:				"npc_tribal_male_soldier"
$Start nav:				"mm_benchmark_sr_$human_nav_10"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"hispanic"

$Human:					"mm_benchmark_sr_$human_11"
$Char type:				"npc_Wong"
$Start nav:				"mm_benchmark_sr_$human_nav_11"
+Group:					"mm_benchmark_sr_$npc_group"

$Human:					"mm_benchmark_sr_$human_12"
$Char type:				"npc_young_female_generic"
$Start nav:				"mm_benchmark_sr_$human_nav_12"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"generic white"

$Human:					"mm_benchmark_sr_$human_13"
$Char type:				"npc_young_female_generic"
$Start nav:				"mm_benchmark_sr_$human_nav_13"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"generic black"

$Human:					"mm_benchmark_sr_$human_14"
$Char type:				"npc_tribal_male_soldier"
$Start nav:				"mm_benchmark_sr_$human_nav_14"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"white"

$Human:					"mm_benchmark_sr_$human_15"
$Char type:				"npc_young_female_generic"
$Start nav:				"mm_benchmark_sr_$human_nav_15"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"generic asian"

$Human:					"mm_benchmark_sr_$human_16"
$Char type:				"npc_tribal_male_soldier"
$Start nav:				"mm_benchmark_sr_$human_nav_16"
+Group:					"mm_benchmark_sr_$npc_group"
+Variant:					"hispanic"

$Human:					"mm_benchmark_sr_$human_17"
$Char type:				"npc_Wong"
$Start nav:				"mm_benchmark_sr_$human_nav_17"
+Group:					"mm_benchmark_sr_$npc_group"

// -------
#Spawn NPC Regions
// -------

// -------
#Action Nodes
// -------

// -------
#Parking
// -------

// -------
#Chunk Streaming Test Cases
// -------

// -------
#Ambients
// -------

// ----------
#DSP Regions
// ----------

// -------------
#Audio Cluders
// -------------

// -------
#Nodes
// -------

// -------
#Searchlights
// -------

// -------
#Movers
// -------

// -------
#Interiors
// -------


#End
