/* eslint-disable strict */
$(function () {
    var listApp = ["#appointment_practitioner_id", "#appointment_start", "#appointment_start_time"];
    $(listApp.join(",")).change(function () {
        $("#dvNoOfApp").addClass("d-none");
        var chkVal = [false, false, false];
        var idx = 0;
        for (const obj of listApp) {
            console.log("obj", obj);
            const val = $(obj).val();
            console.log("val", val);
            if (val && val != undefined && val.length) {
                chkVal[idx] = val;
            }
            idx++;
        }
        const result = chkVal.filter((val) => val == false);
        const queryString = `performer_id=${chkVal[0]}&start_date=${chkVal[1]}&start_time=${chkVal[2]}`;
        console.log("chkVal", chkVal);
        if (result.length == 0) {
            $.ajax({
                url: `/appointment/check?${queryString}`,
                success: function (data) {
                    const resp = JSON.parse(data);
                    $("#dvNoOfApp").removeClass("d-none");
                    $("#NoOfApp").text(resp.count);
                },
            });
        }
    });
});
