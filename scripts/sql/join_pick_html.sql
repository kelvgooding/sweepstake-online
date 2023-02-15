-- pick.html - This will join group code and gn_horses together

SELECT BOMXBX.status, BOMXBX.full_name, gn_horses.h_num, gn_horses.h_name, gn_horses.h_odds, gn_horses.ranked
FROM BOMXBX
LEFT JOIN gn_horses
ON BOMXBX.grp_rank = gn_horses.h_code;
