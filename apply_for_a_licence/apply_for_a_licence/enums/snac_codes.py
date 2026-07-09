from enum import Enum

class SnacCodes(Enum):
    ENGLAND = ["00AA", "00AB", "00AC", "00AD", "00AE", "00AF", "00AG", "00AH", "00AJ", "00AK",
               "00AL", "00AM", "00AN", "00AP", "00AQ", "00AR", "00AS", "00AT", "00AU", "00AW",
               "00AX", "00AY", "00AZ", "00BA", "00BB", "00BC", "00BD", "00BE", "00BF", "00BG",
               "00BH", "00BJ", "00BK", "00BL", "00BM", "00BN", "00BP", "00BQ", "00BR", "00BS",
               "00BT", "00BU", "00BW", "00BX", "00BY", "00BZ", "00CA", "00CB", "00CC", "00CE",
               "00CF", "00CG", "00CH", "00CJ", "00CK", "00CL", "00CM", "00CN", "00CQ", "00CR",
               "00CS", "00CT", "00CU", "00CW", "00CX", "00CY", "00CZ", "00DA", "00DB", "00EB",
               "00EC", "00EE", "00EF", "00EH", "00EJ", "00EM", "00EQ", "00ET", "00EU", "00EW",
               "00EX", "00EY", "00FA", "00FB", "00FC", "00FD", "00FF", "00FK", "00FN", "00FP",
               "00FY", "00GA", "00GF", "00GG", "00GL", "00HA", "00HB", "00HC", "00HD", "00HE",
               "00HF", "00HG", "00HH", "00HN", "00HP", "00HX", "00HY", "00JA", "00KA", "00KB",
               "00KC", "00KF", "00KG", "00LC", "00MA", "00MB", "00MC", "00MD", "00ME", "00MF",
               "00MG", "00ML", "00MR", "00MS", "00MW", "11"  , "11UB", "11UC", "11UE", "11UF",
               "12"  , "12UB", "12UC", "12UD", "12UE", "12UG", "16"  , "16UB", "16UC", "16UD",
               "16UE", "16UF", "16UG", "17"  , "17UB", "17UC", "17UD", "17UF", "17UG", "17UH",
               "17UJ", "17UK", "18"  , "18UB", "18UC", "18UD", "18UE", "18UG", "18UH", "18UK",
               "18UL", "19"  , "19UC", "19UD", "19UE", "19UG", "19UH", "19UJ", "21"  , "21UC",
               "21UD", "21UF", "21UG", "21UH", "22"  , "22UB", "22UC", "22UD", "22UE", "22UF",
               "22UG", "22UH", "22UJ", "22UK", "22UL", "22UN", "22UQ", "23"  , "23UB", "23UC",
               "23UD", "23UE", "23UF", "23UG", "24"  , "24UB", "24UC", "24UD", "24UE", "24UF",
               "24UG", "24UH", "24UJ", "24UL", "24UN", "24UP", "26"  , "26UB", "26UC", "26UD",
               "26UE", "26UF", "26UG", "26UH", "26UJ", "26UK", "26UL", "29"  , "29UB", "29UC",
               "29UD", "29UE", "29UG", "29UH", "29UK", "29UL", "29UM", "29UN", "29UP", "29UQ",
               "30"  , "30UD", "30UE", "30UF", "30UG", "30UH", "30UJ", "30UK", "30UL", "30UM",
               "30UN", "30UP", "30UQ", "31"  , "31UB", "31UC", "31UD", "31UE", "31UG", "31UH",
               "31UJ", "32"  , "32UB", "32UC", "32UD", "32UE", "32UF", "32UG", "32UH", "33"  ,
               "33UB", "33UC", "33UD", "33UE", "33UF", "33UG", "33UH", "34"  , "34UB", "34UC",
               "34UD", "34UE", "34UF", "34UG", "34UH", "36"  , "36UB", "36UC", "36UD", "36UE",
               "36UF", "36UG", "36UH", "37"  , "37UB", "37UC", "37UD", "37UE", "37UF", "37UG",
               "37UJ", "38"  , "38UB", "38UC", "38UD", "38UE", "38UF", "40"  , "40UB", "40UC",
               "40UD", "40UE", "40UF", "41"  , "41UB", "41UC", "41UD", "41UE", "41UF", "41UG",
               "41UH", "41UK", "42"  , "42UB", "42UC", "42UD", "42UE", "42UF", "42UG", "42UH",
               "43"  , "43UB", "43UC", "43UD", "43UE", "43UF", "43UG", "43UH", "43UJ", "43UK",
               "43UL", "43UM", "44"  , "44UB", "44UC", "44UD", "44UE", "44UF", "45"  , "45UB",
               "45UC", "45UD", "45UE", "45UF", "45UG", "45UH", "47"  , "47UB", "47UC", "47UD",
               "47UE", "47UF", "47UG"
               ]

    WALES = ["00NA", "00NC", "00NE", "00NG", "00NJ", "00NL", "00NN", "00NQ", "00NS", "00NU",
             "00NX", "00NZ", "00PB", "00PD", "00PF", "00PH", "00PK", "00PL", "00PM", "00PP",
             "00PR", "00PT"
             ]

    SCOTLAND = ["00QA", "00QB", "00QC", "00QD", "00QE", "00QF", "00QG", "00QH", "00QJ", "00QK",
                "00QL", "00QM", "00QN", "00QP", "00QQ", "00QR", "00QS", "00QT", "00QU", "00QW",
                "00QX", "00QY", "00QZ", "00RA", "00RB", "00RC", "00RD", "00RE", "00RF", "00RG",
                "00RH", "00RJ"
                ]

    NORTHERN_IRELAND = ["95A", "95B", "95C", "95D", "95E", "95F", "95G", "95H", "95I", "95J", "95K",
                        "95L", "95M", "95N", "95O", "95P", "95Q", "95R", "95S", "95T", "95U", "95V",
                        "95W", "95X", "95Y", "95Z"
                        ]

    @staticmethod
    def list():
        values = []
        for member in SnacCodes.__members__.values():
            values += member.value
        return values

