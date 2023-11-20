import textwrap
import base64 as _b64

tutor.qtype_inherit('pythoncode')

checktext = "Show Plot"

defaults["csq_code_post"] = "import matplotlib.pyplot as plt"

def handle_check(submissions, **info):
    """
    This is mostly the same as the default pythoncode handle_check function.
    Difference(s):
        - Catches and ignores the UserWarning made by matplotlib
        - Shows plot in an <img>
    """
    code = get_code(submissions[info["csq_name"]], info)
    if not isinstance(code, str):
        return code

    plot_bytes_code = textwrap.dedent(f'''\
    from io import BytesIO
    import base64 as _b64
    bio = BytesIO()
    plt.savefig(bio, format="png")
    my_base64_pngData = _b64.b64encode(bio.getvalue()).decode('ASCII')
    print("---PLOT BYTES---")
    print(my_base64_pngData, end="")
    ''')

    code = "\n\n".join(["import os\nos.unlink(__file__)", info["csq_code_pre"], code, info["csq_code_post"], plot_bytes_code])

    get_sandbox(info)
    results = info["sandbox_run_code"](
        info, code, info.get("csq_sandbox_options", {}))

    err = info["fix_error_msg"](
        results["fname"], results["err"], info["csq_code_pre"].count(
            "\n") + 2, code
    )

    complete = results.get("info", {}).get("complete", False)

    trunc = False
    outlines = results["out"].split("\n")
    plot_bytes_header, plot_bytes = outlines[-2], outlines[-1]
    outlines = outlines[:-2]
    if len(outlines) > 10:
        trunc = True
        outlines = outlines[:10]
    out = "\n".join(outlines)
    if len(out) >= 5000:
        trunc = True
        out = out[:5000]
    if trunc:
        out += "\n\n...OUTPUT TRUNCATED..."

    timeout = False
    if (not complete) and ("SIGTERM" in err):
        timeout = True
        err = (
            "Your code did not run to completion, "
            "but no error message was returned."
            "\nThis normally means that your code contains an "
            "infinite loop or otherwise took too long to run."
        )

    msg = '<div class="response">'
    if not timeout:
        msg += "<p><b>"
        if complete:
            msg += '<font color="darkgreen">' "Your code ran to completion." "</font>"
            if ".show()" not in code:
                msg += "<br/>Remember to call plt.show() to see your plot!"
            else:
                msg += f'<br/><center><img src="data:image/png;base64,{plot_bytes}" width="80%"/></center>'
        else:
            msg += '<font color="red">' "Your code did not run to completion." "</font>"
        msg += "</b></p>"
    if out != "":
        msg += "\n<p><b>Your code produced the following output:</b>"
        msg += "<br/><pre>%s</pre></p>" % html_format(out)
    if err != "" and "UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown" not in err:
        if not timeout:
            msg += "\n<p><b>Your code produced an error:</b>"
        msg += "\n<br/><font color='red'><tt>%s</tt></font></p>" % html_format(
            err)
    msg += "</div>"

    return msg

def handle_submission(submissions, **info):
    """
    This is mostly the same as the default pythoncode handle_submission function.
    Difference(s):
        - Catches and ignores the UserWarning made by matplotlib
    """
    code = get_code(submissions[info["csq_name"]], info)
    if not isinstance(code, str):
        return code
    if info["csq_use_simple_checker"]:
        if info["csq_result_as_string"]:
            default_checker = _default_string_check_function
        else:
            default_checker = _default_simple_check_function
    else:
        default_checker = _default_check_function
    default_checker = info.get("csq_check_function", default_checker)
    tests = [dict(test_defaults) for i in info["csq_tests"]]
    for i, j in zip(tests, info["csq_tests"]):
        i.update(info["csq_test_defaults"])
        i.update(j)
    show_tests = [i for i in tests if i["include"]]
    if len(show_tests) > 0:
        code = code.rsplit("### Test Cases")[0]

    inp = info["csq_input_check"](code)
    if inp is not None:
        msg = ('<div class="response">' '<font color="red">%s</font>' "</div>") % inp
        return {"score": 0, "msg": msg}

    bak = info["csq_tests"]
    info["csq_tests"] = []
    for i in bak:
        new = dict(test_defaults)
        i.update(info["csq_test_defaults"])
        new.update(i)
        if new["grade"]:
            info["csq_tests"].append(new)

    get_sandbox(info)

    score = 0
    msg = (
        '\n<br/><details%s><summary class="btn btn-catsoop">Show/Hide Detailed Results</summary>'
        % (" open" if info["csq_always_show_tests"] else "")
    )
    msg += (
        '<div class="response" id="%s_result_showhide">' "<h2>Test Results:</h2>"
    ) % (info["csq_name"],)
    test_results = []
    count = 1
    for test in info["csq_tests"]:
        test["result_as_string"] = test.get(
            "result_as_string", info.get("csq_result_as_string", False)
        )
        out, err, log = info["sandbox_run_test"](info, code, test)
        if "cached_result" in test:
            log_s = {
                "result": test["cached_result"],
                "complete": True,
                "duration": 0.0,
                "opcode_count": 0,
                "opcode_limit_reached": False,
            }
            err_s = ""
            out_s = ""
        else:
            out_s, err_s, log_s = info["sandbox_run_test"](info, info["csq_soln"], test)
        if count != 1:
            msg += "\n<p></p><hr/><p></p>"
        msg += "\n<center><h3>Test %02d</h3>" % count
        if test["show_description"]:
            msg += "\n<i>%s</i>" % test["description"]
        msg += "</center><p></p>"
        if test["show_code"]:
            html_code_pieces = [
                i for i in map(lambda x: html_format(test[x]), ["code_pre", "code"])
            ]
            html_code_pieces.insert(1, "#Your Code Here")
            html_code = "<br/>".join(i for i in html_code_pieces if i)
            msg += "\nThe test case was:<br/>\n<p><tt>%s</tt></p>" % html_code
            msg += "<p>&nbsp;</p>"

        result = {"details": log, "out": out, "err": err}
        result_s = {"details": log_s, "out": out_s, "err": err_s}
        if test["variable"] is not None:
            if "result" in log:
                result["result"] = log["result"]
                del log["result"]
            if "result" in log_s:
                result_s["result"] = log_s["result"]
                del log_s["result"]

        checker = test.get("check_function", default_checker)
        try:
            if info["csq_use_simple_checker"]:
                # legacy checker
                check_result = checker(result["result"], result_s["result"])
            else:
                check_result = checker(result, result_s)
        except:
            check_result = 0.0

        if isinstance(check_result, collections.abc.Mapping):
            percentage = check_result["score"]
            extra_msg = check_result["msg"]
        elif isinstance(check_result, collections.abc.Sequence):
            percentage, extra_msg = check_result
        else:
            percentage = check_result
            extra_msg = ""

        test_results.append(percentage)

        imfile = None
        if percentage == 1.0:
            imfile = info["cs_check_image"]
        elif percentage == 0.0:
            imfile = info["cs_cross_image"]

        score += percentage * test["npoints"]

        expected_variable = test["variable"] is not None
        solution_ran = result_s != {}
        submission_ran = result != {}
        show_code = test["show_code"]
        error_in_solution = result_s["err"] != "" and "UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown" not in result_s["err"]
        error_in_submission = result["err"] != "" and "UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown" not in result["err"]
        solution_produced_output = result_s["out"] != ""
        submission_produced_output = result["out"] != ""
        got_submission_result = "result" in result
        got_solution_result = "result" in result_s
        if imfile is None:
            image = ""
        else:
            image = "<img src='%s' />" % imfile

        # report timing and/or opcode count
        if test["show_timing"] == True:
            test["show_timing"] = "%.06f"
        do_timing = test["show_timing"] and "duration" in result_s["details"]
        do_opcount = test["show_opcode_count"] and "opcode_count" in result_s["details"]
        if do_timing or do_opcount:
            msg += "\n<p>"
        if do_timing:
            _timing = result_s["details"]["duration"]
            msg += (
                "\nOur solution ran for %s seconds." % test["show_timing"]
            ) % _timing
        if do_timing and do_opcount:
            msg += "\n<br/>"
        if do_opcount:
            _opcount = result_s["details"]["opcode_count"]
            msg += "\nOur solution executed %s Python opcodes.<br/>" % _opcount
        if do_timing or do_opcount:
            msg += "\n</p>"

        if expected_variable and show_code:
            if got_solution_result:
                msg += (
                    "\n<p>Our solution produced the following value for <tt>%s</tt>:"
                ) % test["variable"]
                m = test["transform_output"](result_s["result"])
                msg += "\n<br/><font color='blue'>%s</font></p>" % m
            else:
                msg += (
                    "\n<p>Our solution did not produce a value for <tt>%s</tt>.</p>"
                ) % test["variable"]

        if solution_produced_output and show_code:
            msg += "\n<p>Our code produced the following output:"
            msg += "<br/><pre>%s</pre></p>" % html_format(result_s["out"])

        if error_in_solution and test["show_stderr"]:
            msg += "\n<p><b>OOPS!</b> Our code produced an error:"
            e = html_format(result_s["err"])
            msg += "\n<br/><font color='red'><tt>%s</tt></font></p>" % e

        if show_code:
            msg += "<p>&nbsp;</p>"

        # report timing and/or opcode count
        do_timing = test["show_timing"] and "duration" in result["details"]
        do_opcount = test["show_opcode_count"] and "opcode_count" in result["details"]
        if do_timing or do_opcount:
            msg += "\n<p>"
        if do_timing:
            _timing = result["details"]["duration"]
            msg += (
                "\nYour solution ran for %s seconds." % test["show_timing"]
            ) % _timing
        if do_timing and do_opcount:
            msg += "\n<br/>"
        if do_opcount:
            _opcount = result["details"]["opcode_count"]
            msg += "\nYour code executed %d Python opcodes.<br/>" % _opcount
        if do_timing or do_opcount:
            msg += "\n</p>"

        if expected_variable and show_code:
            if got_submission_result:
                msg += (
                    "\n<p>Your submission produced the following value for <tt>%s</tt>:"
                ) % test["variable"]
                m = test["transform_output"](result["result"])
                msg += "\n<br/><font color='blue'>%s</font>%s</p>" % (m, image)
            else:
                msg += (
                    "\n<p>Your submission did not produce a value for <tt>%s</tt>.</p>"
                ) % test["variable"]
        else:
            msg += "\n<center>%s</center>" % (image)

        if submission_produced_output and show_code:
            msg += "\n<p>Your code produced the following output:"
            msg += "<br/><pre>%s</pre></p>" % html_format(result["out"])

        if error_in_submission and test["show_stderr"]:
            msg += "\n<p>Your submission produced an error:"
            e = html_format(result["err"])
            msg += "\n<br/><font color='red'><tt>%s</tt></font></p>" % e
            msg += "\n<br/><center>%s</center>" % (image)

        if extra_msg:
            msg += "\n<p>%s</p>" % extra_msg

        count += 1

    msg += "\n</div></details>"
    tp = total_test_points(**info)
    overall = float(score) / tp if tp != 0 else 0
    hint_func = info.get("csq_hint")
    if hint_func:
        try:
            hint = hint_func(test_results, code, info)
            msg += hint or ""
        except Exception as err:
            pass
    if info["csq_show_check"]:
        if overall == 1.0:
            checkimg = '<img src="%s" />' % info["cs_check_image"]
        elif overall == 0.0:
            checkimg = '<img src="%s" />' % info["cs_cross_image"]
        else:
            checkimg = ""
    else:
        checkimg = ""
    msg = (
        (
            ("\n<br/>&nbsp;Your score on your most recent " "submission was: %01.02f%%")
            % (overall * 100)
        )
        + checkimg
        + msg
    )
    out = {"score": overall, "msg": msg}
    return out
